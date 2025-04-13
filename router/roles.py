from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from models import Role, User,ChatSession
from database import get_db
from repository import get_role_or_404, delete_role, get_roles_by_user
from utils.auth import get_current_user
import os, shutil
from urllib.parse import urljoin

router = APIRouter(prefix="/api/roles", tags=["角色"])

UPLOAD_DIR = "uploads"
@router.post("/create")
async def create_role(
    name: str = Form(...),
    age: int = Form(None),
    occupation: str = Form(None),
    description: str = Form(None),
    personality: str = Form(None),
    speaking_style: str = Form(None),
    hobbies: str = Form(None),
    worldview: str = Form(None),
    category: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ 新增這行
):
    image_filename = None
    if image:
        image_filename = f"{UPLOAD_DIR}/{image.filename}"
        with open(image_filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    new_role = Role(
        name=name,
        age=age,
        occupation=occupation,
        description=description,
        personality=personality,
        speaking_style=speaking_style,
        hobbies=hobbies,
        worldview=worldview,
        category=category,
        image=image_filename,
        user_id=current_user.id   # ✅ 重點：記錄是哪個使用者創的
    )

    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.get("/list")
def get_roles(request: Request, db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    for role in roles:
        if role.image:
            clean_path = role.image.lstrip("/")
            role.image = urljoin(str(request.base_url), clean_path)
    return roles

@router.get("/my")
def get_my_roles(request: Request,db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    roles = get_roles_by_user(db, current_user.id)
    
    for role in roles:
        if role.image:
            clean_path = role.image.lstrip("/")
            role.image = urljoin(str(request.base_url), clean_path)
    return [{
        "id": r.id,
        "name": r.name,
        "age": r.age,
        "occupation": r.occupation,
        "description": r.description,
        "image": r.image,
    } for r in roles]


@router.get("/public")
def get_public_roles(request: Request, db: Session = Depends(get_db)):
    roles = db.query(Role).filter(Role.is_public == True).all()
    for role in roles:
        if role.image:
            clean_path = role.image.lstrip("/")
            role.image = urljoin(str(request.base_url), clean_path)
    return roles

@router.get("/chatting")
def get_chatting_roles(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 找出該使用者的所有聊天記錄
    session_query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    role_ids = list({session.role_id for session in session_query})  # 用 set 去重複

    # 查出角色資訊
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    for role in roles:
        if role.image:
            clean_path = role.image.lstrip("/")
            role.image = urljoin(str(request.base_url), clean_path)
    return roles

@router.get("/{id}")
def get_role(id: int, request: Request, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    image_url = f"{request.base_url}{role.image}" if role.image else None
    return {
        "id": role.id,
        "name": role.name,
        "age": role.age,
        "occupation": role.occupation,
        "description": role.description,
        "personality": role.personality,
        "speaking_style": role.speaking_style,
        "hobbies": role.hobbies,
        "worldview": role.worldview,
        "category": role.category,
        "image": image_url
    }

@router.put("/update/{id}")
async def update_role(
    id: int,
    name: str = Form(...),
    age: int = Form(None),
    occupation: str = Form(None),
    description: str = Form(None),
    personality: str = Form(None),
    speaking_style: str = Form(None),
    hobbies: str = Form(None),
    worldview: str = Form(None),
    category: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    role = db.query(Role).filter(Role.id == id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if image:
        ext = image.filename.split('.')[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "gif"]:
            raise HTTPException(status_code=400, detail="只允許上傳圖片")
        filename = f"{UPLOAD_DIR}/{id}.{ext}"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        role.image = filename

    role.name = name
    role.age = age
    role.occupation = occupation
    role.description = description
    role.personality = personality
    role.speaking_style = speaking_style
    role.hobbies = hobbies
    role.worldview = worldview
    role.category = category

    db.commit()
    db.refresh(role)
    return role

@router.delete("/delete/{id}")
def delete_role_api(id: int, db: Session = Depends(get_db)):
    role = get_role_or_404(db, id)
    delete_role(db, id)
    return {"message": f"角色 {role.name} 已刪除"}

