from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL

url = URL.create(
    drivername="mysql+mysqlconnector",
    username="User",
    password="User$1234",  # 這裡可直接放原文，不需手動編碼
    host="tpe1.clusters.zeabur.com",
    port=21004,
    database="dreamlinker",
    query={"charset": "utf8mb4"},
)

engine = create_engine(url, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
