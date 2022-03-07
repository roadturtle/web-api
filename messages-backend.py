import asyncio
import datetime
from xmlrpc.client import DateTime
import databases
import sqlalchemy
from importlib.metadata import metadata
from fastapi import FastAPI, Path, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./messages.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

messages = sqlalchemy.Table(
    "messages",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("author", sqlalchemy.String),
    sqlalchemy.Column("text", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

class MessageIn(BaseModel):
    author: str
    text: str

class Message(BaseModel):
    id: int
    author: str
    text: str

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()
    #current_message_id = len(list(await database.fetch_all(messages.select()))) - 1

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/messages/", response_model=List[Message])
async def read_messages():
    query = messages.select()
    message_list = list(await database.fetch_all(query))
    print(len(message_list))
    return await database.fetch_all(query)

@app.post("/messages/", response_model=Message)
async def create_message(message: MessageIn):
    query = messages.insert().values(author=message.author, text=message.text)
    last_record_id = await database.execute(query)
    return {**message.dict(), "id": last_record_id}

