from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 從環境變數讀取連線資訊（部署時更安全）
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "LvIKOhEJjuRIqPefDjnitvwQnoRKepTy")
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "railway")

# 建立連線字串
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 建立資料庫引擎
engine = create_engine(DATABASE_URL, echo=True)

# 建立 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定義 ORM 的 Base 類別
Base = declarative_base()

# 🚀 建立資料表
def init_db():
    from models import Base  # 避免循環引用
    Base.metadata.create_all(bind=engine)

# 取得 DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
