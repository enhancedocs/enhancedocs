from dotenv import load_dotenv
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from .config import Config

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

from .routers import integrations, ingest, ask

app.include_router(ask.router)
app.include_router(ingest.router)
app.include_router(integrations.router)
