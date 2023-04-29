import json
import faiss
import pickle

from dotenv import load_dotenv
from typing import Optional, List
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT)
from langchain.chains.llm import LLMChain
from langchain.chains import ConversationalRetrievalChain
from pydantic import BaseModel

import utils
from config import Config
from langchain.vectorstores import Qdrant
load_dotenv()
config = Config()

app = FastAPI()


embedding = OpenAIEmbeddings()
llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.put("/ingest")
async def ingest_endpoint(request: Request, credentials: str = Depends(utils.verify_api_key)):
    source_chunks = []
    splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
    content = await request.body()
    content_str = content.decode('utf-8')
    lines = content_str.splitlines()
    for line in lines:
        line = json.loads(line)
        for chunk in splitter.split_text(line["content"]):
            source_chunks.append(Document(page_content=chunk, metadata={"source": line["source"]}))
    if config.is_external_db_used():
        Qdrant.from_documents(
            documents=source_chunks,
            embedding=embedding,
            collection_name=config.default_collection_name,
            **config.qdrant_args
        )
    else:
        store = FAISS.from_documents(source_chunks, OpenAIEmbeddings())
        faiss.write_index(store.index, config.vector_index_file_path)
        store.index = None
        with open(config.vector_store_file_path, "wb") as f:
            pickle.dump(store, f)
    return {"message": "Data ingested successfully"}


class AskModel(BaseModel):
    question: str
    history: List[str]


@app.post("/ask")
def ask_endpoint(body: AskModel, credentials: str = Depends(utils.verify_access_token)):
    if utils.is_db_empty(config):
        raise HTTPException(status_code=404, detail="No data found. Ingest data using "
                                                    "https://github.com/enhancedocs/cli or the API directly")
    store = utils.get_vector_store(config)
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_with_sources_chain(llm, chain_type="stuff", prompt=config.prompt)
    chain = ConversationalRetrievalChain(
        combine_docs_chain=doc_chain,
        retriever=store.as_retriever(),
        question_generator=question_generator,
        get_chat_history=utils.get_chat_history,
        return_source_documents=True
    )
    result = chain(
        {"question": body.question, "project_name": config.project_name, "chat_history": body.history},
        return_only_outputs=True
    )
    sources = []
    for document in result['source_documents']:
        if utils.docusaurus_source_filter(document):
            sources.append(utils.format_docusaurus_source(document.metadata["source"], config.docs_base_url))
    return {"answer": result["answer"], "sources": sources}


@app.get("/ask")
def ask_endpoint(question: str, credentials: str = Depends(utils.verify_access_token)):
    if utils.is_db_empty(config):
        raise HTTPException(status_code=404, detail="No data found. Ingest data using "
                                                    "https://github.com/enhancedocs/cli or the API directly")
    store = utils.get_vector_store(config)
    qa_chain = load_qa_with_sources_chain(llm, chain_type="stuff", prompt=config.prompt)
    chain = RetrievalQAWithSourcesChain(
        combine_documents_chain=qa_chain,
        retriever=store.as_retriever(),
        return_source_documents=True
    )
    result = chain({"question": question, "project_name": config.project_name}, return_only_outputs=True)
    sources = []
    for document in result['source_documents']:
        if utils.docusaurus_source_filter(document):
            sources.append(utils.format_docusaurus_source(document.metadata["source"], config.docs_base_url))
    return {"answer": result["answer"], "sources": sources}


@app.post("/integrations/slack/events")
async def handle_slack_event(request: Request):
    if config.slack_client is None:
        raise HTTPException(status_code=404, detail="Slack Integration not enabled")
    return await config.slack_client.handler.handle(request)
