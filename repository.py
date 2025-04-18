from sqlalchemy.orm import Session
import models, schemas
from router import auth

# 查詢所有角色
def get_roles(db: Session):
    return db.query(models.Role).all()

# 查詢我的角色
def get_roles_by_user(db: Session, user_id: int):
    return db.query(models.Role).filter(models.Role.user_id == user_id).all()

# 查詢單一角色
def get_role_by_id(db: Session, role_id: int):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

# 新增角色
def create_role(db: Session, role: schemas.RoleCreate):
    new_role = models.Role(**role.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# 更新角色
def update_role(db: Session, role_id: int, role_update: schemas.RoleCreate):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        return None  # 如果角色不存在，回傳 None
    
    # 更新角色資料
    for key, value in role_update.dict().items():
        setattr(role, key, value)  # 動態更新屬性

    db.commit()
    db.refresh(role)
    return role  # 回傳更新後的角色

# 刪除角色
def delete_role(db: Session, role_id: int):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        return None
    db.delete(role)
    db.commit()
    return role
from fastapi import HTTPException

# 通用函式：檢查角色是否存在，否則拋出 404 錯誤
def get_role_or_404(db: Session, role_id: int):
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


# 取得所有記憶（可擴充條件過濾）
def get_memories(db: Session):
    return db.query(models.Memory).all()

# 取得單筆
def get_memory_by_id(db: Session, memory_id: int):
    return db.query(models.Memory).filter(models.Memory.id == memory_id).first()

# 建立
def create_memory(db: Session, memory: schemas.MemoryCreate):
    db_memory = models.Memory(**memory.dict())
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory

# 更新
def update_memory(db: Session, memory_id: int, memory: schemas.MemoryUpdate):
    db_memory = db.query(models.Memory).filter(models.Memory.id == memory_id).first()
    if db_memory:
        for key, value in memory.dict(exclude_unset=True).items():
            setattr(db_memory, key, value)
        db.commit()
        db.refresh(db_memory)
    return db_memory

# 刪除
def delete_memory(db: Session, memory_id: int):
    db_memory = db.query(models.Memory).filter(models.Memory.id == memory_id).first()
    if db_memory:
        db.delete(db_memory)
        db.commit()
    return db_memory


# 取得所有事件
def get_events(db: Session):
    return db.query(models.Event).all()

# 取得單筆事件
def get_event_by_id(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

# 新增事件
def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# 更新事件
def update_event(db: Session, event_id: int, event: schemas.EventUpdate):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        for key, value in event.dict(exclude_unset=True).items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
    return db_event

# 刪除事件
def delete_event(db: Session, event_id: int):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event


def get_sessions(db: Session):
    return db.query(models.ChatSession).all()

def get_session_by_id(db: Session, session_id: int):
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def create_session(db: Session, session: schemas.ChatSessionCreate):
    db_session = models.ChatSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Session, session_id: int, session: schemas.ChatSessionUpdate):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if db_session:
        for key, value in session.dict(exclude_unset=True).items():
            setattr(db_session, key, value)
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: int):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
    return db_session

# repository.py
# 聊天頁取得角色資訊
def get_role_by_session(db: Session, session_id: int):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        return None
    role = db.query(models.Role).filter(models.Role.id == session.role_id).first()
    return role



def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str):
    user = models.User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 新增
def create_model_api(db, user_id: int, data):
    new_api = models.ModelAPI(
        user_id=user_id,
        name=data.name,
        provider=data.provider,
        config=data.config
    )
    db.add(new_api)
    db.commit()
    db.refresh(new_api)
    return new_api

# 查詢某使用者的全部金鑰
def get_model_apis_by_user(db, user_id: int):
    return db.query(models.ModelAPI).filter_by(user_id=user_id).all()

# 更新金鑰（名稱、config、啟用狀態）
def update_model_api(db, api_id: int, data):
    api = db.query(models.ModelAPI).filter_by(id=api_id).first()
    if not api:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(api, key, value)
    db.commit()
    db.refresh(api)
    return api

# 刪除
def delete_model_api(db, api_id: int):
    api = db.query(models.ModelAPI).filter_by(id=api_id).first()
    if not api:
        return None
    db.delete(api)
    db.commit()
    return api