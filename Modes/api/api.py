import os
import sys

from llama_cpp import Llama

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from .models import User, Conversation
import uvicorn


import random
import string
import json


from datetime import datetime


sys.path.append('../Llama')

key = 1488

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None

class ImageRequest(BaseModel):
    image_path: str

class Conversations(BaseModel):
    num: int
    conversations: list

def loadChatLLama():
    from Llama.llama import ChatLLama
    return ChatLLama

def encrypt(message, key):
    # Step 1: Reverse the message
    reversed_message = message[::-1]
    
    # Step 2: Perform a Caesar cipher shift on the reversed message
    shifted_message = ''
    for char in reversed_message:
        shifted_char = chr((ord(char) + key) % 256)  # Shift by key, wrap around ASCII range
        shifted_message += shifted_char
    
    # Step 3: Convert characters to their ASCII values and concatenate
    encrypted_message = '-'.join(str(ord(char)) for char in shifted_message)
    
    return encrypted_message

def decrypt(encrypted_message, key):
    # Step 1: Split the message into individual ASCII values
    ascii_values = encrypted_message.split('-')
    
    # Step 2: Convert ASCII values back to characters and concatenate
    shifted_message = ''.join(chr(int(val)) for val in ascii_values)
    
    # Step 3: Undo the Caesar cipher shift
    reversed_message = ''
    for char in shifted_message:
        original_char = chr((ord(char) - key) % 256)  # Undo the shift
        reversed_message += original_char
    
    # Step 4: Reverse the message back to its original form
    decrypted_message = reversed_message[::-1]
    
    return decrypted_message

def generate_unique_id(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = db.query(User).filter(User.username == decrypt(token, key)).first()
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

def get_llama():
    return llama

def generate_response(llama, conservation_id, message, db):
    # Get previous messages
    conversation = db.query(Conversation).filter(Conversation.id == conservation_id).first()
    
    conversation.add_message("user", message)
        
    previous_messages = json.loads(conversation.messages)
    formatted_message = ChatLLama.chatcompletionformat("user", message)
    
    formatted_message = ChatLLama.chatcompletionformat("user", message)
    new_message = ChatLLama.msggen(llama, previous_messages, formatted_message)
    
    conversation.add_message("assistant", new_message)
    
    db.commit()
    return new_message


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = encrypt(user.username, key)  # In a real app, generate a secure token
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first() 
    db_email = db.query(User).filter(User.email == user.email).first() 
    if db_user or db_email:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=User.hash_password(user.password),
        disabled=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return HTMLResponse(status_code=200)

@app.post("/chat")
async def chat(message: str, conversation_id: str, token: str = Depends(oauth2_scheme), llama=Depends(get_llama),  db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    print(message)
    print(conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    
    
    formatted_message = ChatLLama.chatcompletionformat("user", message)

    response = generate_response(llama, conversation_id, message, db)
    
    return {"response": response}

@app.post("/create-conversation")
def create_conversation(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    conversation_id = generate_unique_id()
    new_conversation = Conversation(id=conversation_id, user_token=user.username, creation_time=datetime.utcnow())
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return {"conversation_id": new_conversation.id}

@app.post("/get-conversations", response_model=Conversations )
def get_conversation(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    conversations = db.query(Conversation).filter(Conversation.user_token == user.username).all()
    conversation_count = len(conversations)
    Conversationout = Conversations()
    Conversationout.num = conversation_count
    Conversationout.conversations = conversations
    return Conversationout
    
def run():
    uvicorn.run(app, host='0.0.0.0', port=8000)

def api(llamai : Llama):
    global llama
    global ChatLLama
    llama = llamai
    
    ChatLLama = loadChatLLama()
    
    print("Loaded!")
    
    run()