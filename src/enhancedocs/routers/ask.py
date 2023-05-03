from fastapi import APIRouter, Depends, HTTPException
from typing import List
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT)
from langchain.chains.llm import LLMChain
from langchain.chains import ConversationalRetrievalChain
from pydantic import BaseModel

from ..main import config, llm
from .. import utils


class AskModel(BaseModel):
    question: str
    history: List[str]


router = APIRouter(tags=["ask"])


@router.post("/ask")
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


@router.get("/ask")
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
