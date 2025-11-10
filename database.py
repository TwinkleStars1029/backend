from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base
import os

url = URL.create(
    drivername="mysql+mysqlconnector",
    username="User",
    password="User%1234",  
    host="tpe1.clusters.zeabur.com",
    port=21004,
    database="my_chat_app",  
    query={"charset": "utf8mb4"},
)

# 建立連線字串
engine = create_engine(url, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🚀 建立資料表
def init_db():
    from models import Base  
    Base.metadata.create_all(bind=engine)

# 取得 DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
