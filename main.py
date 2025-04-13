from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Backend is working!"}



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from database import init_db
# from models import Base
# from database import engine
# import os

# # 載入路由模組
# from router import auth, chat, roles, memories, events, sessions, model_api

# app = FastAPI()

# # 設定 CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 提供圖片靜態路徑
# UPLOAD_DIR = "uploads"
# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)
# app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# # 建立資料表
# Base.metadata.create_all(bind=engine)

# # 啟動時初始化 DB
# @app.on_event("startup")
# def startup_event():
#     init_db()

# # 載入各個路由模組
# app.include_router(auth.router)
# app.include_router(roles.router)
# app.include_router(chat.router)
# app.include_router(memories.router)
# app.include_router(events.router)
# app.include_router(sessions.router)
# app.include_router(model_api.router)
