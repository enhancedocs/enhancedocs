import os
import faiss
import pickle
import json
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from langchain import OpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
from langchain import PromptTemplate

import utils

load_dotenv()
app = FastAPI()

llm = OpenAI(temperature=0.7, model_name="gpt-3.5-turbo")


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
    store = FAISS.from_documents(source_chunks, OpenAIEmbeddings())
    faiss.write_index(store.index, "data/vectorstore.index")
    store.index = None
    os.makedirs("data", exist_ok=True)
    with open("data/vectorstore.pkl", "wb") as f:
        pickle.dump(store, f)
    return {"message": "Data ingested successfully"}


@app.get("/ask")
def ask_endpoint(question: str, credentials: str = Depends(utils.verify_access_token)):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    index = faiss.read_index("data/vectorstore.index")
    with open("data/vectorstore.pkl", "rb") as f:
        store = pickle.load(f)
    store.index = index
    prompt = PromptTemplate(
        template=config["prompt_template"], input_variables=["summaries", "question"]
    )
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=store.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )
    result = chain({"question": question}, return_only_outputs=True)
    return result
