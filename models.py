from sqlalchemy import Column, Integer, String, Text, DateTime, TIMESTAMP,ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from datetime import datetime


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    occupation = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    speaking_style = Column(Text, nullable=True)
    hobbies = Column(Text, nullable=True)
    worldview = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    image = Column(String(255), nullable=True)  # 新增圖片欄位
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    



# 1. ChatSession 對話會話表
# class ChatSession(Base):
#     __tablename__ = "chat_sessions"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

#     messages = relationship("ChatMessage", back_populates="session")
#     memories = relationship("ChatMemory", back_populates="session")

# 2. ChatMessage 對話訊息表
# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     talk_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
#     sender = Column(Enum("user", "assistant"), nullable=False)
#     message = Column(Text, nullable=False)
#     timestamp = Column(TIMESTAMP, default=datetime.utcnow)

#     session = relationship("ChatSession", back_populates="messages")

# 3. ChatMemory 長期記憶表
class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    talk_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True)
    memory_text = Column(Text, nullable=False)
    is_important = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="memories")

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     username = Column(String(50), unique=True, nullable=False)
#     created_at = Column(TIMESTAMP, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    talk_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(Enum("user", "assistant", name="sender_enum"), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    # 建立與 `chat_sessions` 的關聯
    talk = relationship("ChatSession", back_populates="messages")



class Memory(Base):
    __tablename__ = "memory_memories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text)
    token_count = Column(Integer, default=0)
    section = Column(String(100))
    selected = Column(Boolean, default=False)
    tags = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Event(Base):
    __tablename__ = "memory_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    title = Column(String(100))
    description = Column(Text)
    date = Column(String(100))
    tags = Column(String(255))
    is_active = Column(Boolean, default=True)
    selected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    rule = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer)
    sessions_input = Column(Text)
    messages = relationship("ChatMessage", back_populates="talk", cascade="all, delete-orphan")
    memories = relationship("ChatMemory", back_populates="session")
    title = Column(String(255), nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_apis = relationship("ModelAPI", back_populates="user", cascade="all, delete")


class ModelAPI(Base):
    __tablename__ = "model_apis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)            # 顯示名稱（自訂）
    provider = Column(String(50), nullable=False)         # 模型平台，例如 azure、gemini
    config = Column(JSON, nullable=False)                 # 儲存參數 JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="model_apis")


# class ChatSession(Base):
#     __tablename__ = "chat_sessions"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
#     # 新增關聯：一個對話 session 可以有多條訊息
#     messages = relationship("ChatMessage", back_populates="talk", cascade="all, delete-orphan")
#     memories = relationship("ChatMemory", back_populates="session")