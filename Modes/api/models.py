from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from .database import Base
from datetime import datetime
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    user_token = Column(String, ForeignKey("users.username"))
    creation_time = Column(DateTime, default=datetime.utcnow)
    messages = Column(String, default="[]")  # Store messages as JSON string

    def add_message(self, role, message_content):
        messages = json.loads(self.messages)
        messages.append({"role": role, "content": message_content})
        self.messages = json.dumps(messages)
