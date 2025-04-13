from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
# 定義角色請求的 Schema
class RoleCreate(BaseModel):
    name: str
    age: Optional[int] = None
    occupation: Optional[str] = None
    description: Optional[str] = None
    basic_info: Optional[str] = None
    personality: Optional[str] = None
    speaking_style: Optional[str] = None
    hobbies: Optional[str] = None
    worldview: Optional[str] = None
    category: Optional[str] = None

class ChatRequest(BaseModel):
    talk_id: int
    user_message: str
    max_tokens: int 
    temperature: float 
    top_p: float
    presence_penalty: float
    frequency_penalty: float
    model_api_id: Optional[int] = None
    

class ChatResponse(BaseModel):
    talk_id: int
    user_message_id: int
    assistant_message_id: int
    assistant_message: str
    timestamp: str
# 單筆聊天訊息結構
class ChatMessageSchema(BaseModel):
    id: int
    sender: str
    message: str
    timestamp: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允許 Pydantic 直接從 ORM 轉換

# 讀取歷史對話 API 回應格式
class ChatHistoryResponse(BaseModel):
    talk_id: int
    messages: List[ChatMessageSchema]
    has_more: bool

# 更新訊息 API 的請求格式
class UpdateMessageRequest(BaseModel):
    new_message: str

class MemoryBase(BaseModel):
    role_id: int
    session_id: int
    content: Optional[str] = None
    token_count: Optional[int] = 0
    section: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = True
    selected: Optional[bool] = False

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    role_id: Optional[int] = None
    session_id: Optional[int] = None
    content: Optional[str] = None
    token_count: Optional[int] = None
    section: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None
    selected: Optional[bool] = False

class MemoryOut(MemoryBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class EventBase(BaseModel):
    role_id: int
    session_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = True
    selected: Optional[bool] = False

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    role_id: int
    session_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = True
    selected: Optional[bool] = False

class EventOut(EventBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    role_id: int
    rule: Optional[str] = None
    is_active: Optional[bool] = True
    user_id: Optional[int] = None
    sessions_input: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(ChatSessionBase):
    role_id: Optional[int] = None
    rule: Optional[str] = None
    sessions_input: Optional[str] = None
    title: Optional[str] = None

class ChatSessionOut(ChatSessionBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RoleSchema(BaseModel):
    id: int
    name: str
    age: Optional[int]
    occupation: Optional[str]
    description: Optional[str]
    image: Optional[str]

    class Config:
        orm_mode = True

class ChatSessionOut(BaseModel):
    id: int
    role_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    title: Optional[str] = None 
    rule: Optional[str] = None

    class Config:
        orm_mode = True

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfo(BaseModel):
    id: int
    username: str
    created_at: datetime   

    class Config:
        orm_mode = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ModelAPIBase(BaseModel):
    name: str
    provider: str
    config: Dict[str, str]

class ModelAPICreate(ModelAPIBase):
    pass

class ModelAPIUpdate(BaseModel):
    name: str | None = None
    config: Dict[str, str] | None = None
    is_active: bool | None = None

class ModelAPIOut(ModelAPIBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2