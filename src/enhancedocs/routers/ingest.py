import json
import faiss
import pickle

from fastapi import APIRouter, Request, Depends
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores import Qdrant

from ..main import config, embedding
from .. import utils

router = APIRouter(tags=["ingest"])


@router.put("/ingest")
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
        store = FAISS.from_documents(source_chunks, embedding)
        faiss.write_index(store.index, config.vector_index_file_path)
        store.index = None
        with open(config.vector_store_file_path, "wb") as f:
            pickle.dump(store, f)
    return {"message": "Data ingested successfully"}
