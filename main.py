from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db
from models import Base
from database import engine
import os
import uvicorn
import logging

# 建立 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()  # 改為印到 console，適合 Railway
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 建立 FastAPI app
app = FastAPI()

# CORS 設定（允許所有前端來源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 靜態資源路由（上傳圖檔）
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 資料庫建表
Base.metadata.create_all(bind=engine)

# app 啟動時會執行 DB 初始化
@app.on_event("startup")
def startup_event():
    logger.info("🚀 應用啟動中，初始化資料庫")
    init_db()

# 測試首頁（可用於健康檢查）
@app.get("/")
def ping():
    logger.info("✅ ping 成功，後端正常運作中")
    return {"status": "ok"}

# 載入 router 模組
from router import auth, chat, roles, memories, events, sessions, model_api
app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(chat.router)
app.include_router(memories.router)
app.include_router(events.router)
app.include_router(sessions.router)
app.include_router(model_api.router)

# 支援 python main.py 啟動（本地測試）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"✅ 本地啟動 uvicorn：port={port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
