from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# MySQL 連線資訊（請依照你的設定調整）
DATABASE_URL = "mysql+pymysql://root:User$1234@127.0.0.1:3306/my_chat_app"

# 建立資料庫引擎
engine = create_engine(DATABASE_URL, echo=True)

# 建立 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 定義 ORM 的 Base 類別
Base = declarative_base()


# 🚀 在這裡建立資料庫表
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