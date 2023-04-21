import os
import json
import shutil
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain import OpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain import PromptTemplate
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.vectorstores import Chroma
import utils
from config import Config
import chromadb

config = Config()

chroma_settings = chromadb.config.Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=config.data_path
)
chroma_client = chromadb.Client(chroma_settings)

load_dotenv()
app = FastAPI()

llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
embedding = OpenAIEmbeddings()

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
    try:
        chroma_client.delete_collection(config.chroma_collection_name)
        chroma_client.persist()
    except IndexError:
        pass
    Chroma.from_documents(
        documents=source_chunks,
        embedding=embedding,
        persist_directory=config.data_path,
        collection_name=config.chroma_collection_name
    )
    return {"message": "Data ingested successfully"}


@app.get("/ask")
def ask_endpoint(question: str, credentials: str = Depends(utils.verify_access_token)):
    if not os.listdir(config.data_path):
        raise HTTPException(status_code=404, detail="No data found. Ingest data using "
                                                    "https://github.com/enhancedocs/cli or the API directly")
    store = Chroma(
        persist_directory=config.data_path,
        embedding_function=embedding,
        collection_name=config.chroma_collection_name
    )
    prompt = PromptTemplate(template=config.prompt_template, input_variables=["summaries", "question"])
    qa_chain = load_qa_with_sources_chain(llm, chain_type="stuff", prompt=prompt)
    chain = RetrievalQAWithSourcesChain(
        combine_documents_chain=qa_chain,
        retriever=store.as_retriever(),
        return_source_documents=True
    )
    result = chain({"question": question}, return_only_outputs=True)
    sources = []
    for document in result['source_documents']:
        if utils.docusaurus_source_filter(document):
            sources.append(utils.format_docusaurus_source(document.metadata["source"], config.docs_base_url))
    return {"answer": result["answer"], "sources": sources}
