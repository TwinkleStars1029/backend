# router/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas
import repository
from utils.auth import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user
)

from models import User

router = APIRouter(prefix="/auth", tags=["auth"])

# 🔐 註冊會員
@router.post("/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = repository.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="使用者名稱已存在")
    hashed_pw = hash_password(user.password)
    repository.create_user(db, user.username, hashed_pw)
    return {"message": "註冊成功"}

# 🔐 登入會員
@router.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    print("登入帳號：", user.username)
    db_user = repository.get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    token = create_access_token(data={"user_id": db_user.id, "username": db_user.username})
    print("登入帳號：", user.username)
    print("查到使用者：", db_user.username if db_user else "None")
    print("密碼是否正確：", verify_password(user.password, db_user.password))
    return {"access_token": token, "token_type": "bearer"}

# 🔐 取得當前使用者
@router.get("/me", response_model=schemas.UserInfo)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
