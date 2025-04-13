import openai
import os
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import ChatSession, ChatMessage, Memory, ModelAPI
from schemas import ChatRequest, ChatResponse,ChatHistoryResponse,UpdateMessageRequest
from dotenv import load_dotenv
from datetime import datetime
from schemas import RoleSchema
from repository import get_role_by_session


# import opencc 
# converter = opencc.OpenCC('s2t')

router = APIRouter()

load_dotenv()

@router.post("/api/chat/send", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    用戶發送訊息，後端處理後回應 AI 內容
    """
    # 嘗試獲取 talk_id，若不存在則建立新的對話
    session = db.query(ChatSession).filter(ChatSession.id == request.talk_id).first()
    if not session:
        new_session = ChatSession(user_id=1, role_id=1)  # 預設 user_id 和 role_id
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session = new_session  # 讓 session 變成剛剛建立的對話
        request.talk_id = new_session.id  # 更新 talk_id，確保後續查詢成功

    # 取得最近 10 條短期記憶
    recent_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.talk_id == request.talk_id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(10)
        .all()
    )

    # 整合 Prompt
    prompt_messages = []
    
    # 整合 Prompt 初始化
    prompt_messages = [{
        "role": "system",
        "content": "請和使用者玩戀愛角色扮演遊戲，請模仿角色性格，參考發生過的事件、回憶，以角色的角度回覆對話，請始終使用繁體中文回應使用者，回應內容必須符合以下對話規則，回覆字數接近500但不超過500。"
    }]

    # 決定使用哪種記憶來源：sessions_input 或 ChatMemory
    use_session_input = getattr(request, "use_session_input", True)

    if use_session_input:
        # ✅ 使用 chat_sessions.sessions_input 內容
        if session.sessions_input:
            prompt_messages.append({
                "role": "system",
                "content": session.sessions_input
            })
    else:
        # 取得長期記憶 (重要記憶)
        important_memories = (
            db.query(Memory)
            .filter(Memory.session_id == session.id, Memory.is_active == True)
            .all()
        )
        # ✅ 改為加入 ChatMemory 記憶（保留原有邏輯）
        for memory in important_memories:
            prompt_messages.append({
                "role": "system",
                "content": f"重要記憶：{memory.memory_text}"
            })
    
    for msg in reversed(recent_messages):  # 逆序，讓最新對話在最下方
        prompt_messages.append({"role": msg.sender, "content": msg.message})

    # 加入用戶最新的輸入
    prompt_messages.append({"role": "user", "content": request.user_message})

    model_api = db.query(ModelAPI).filter(ModelAPI.id == request.model_api_id).first()
    if not model_api:
        print("模型金鑰不存在")
        raise HTTPException(status_code=404, detail="模型金鑰不存在")

    provider = model_api.provider
    config = model_api.config

    
    if not provider:
        raise HTTPException(status_code=400, detail="模型 provider 為空")
    if not config:
        raise HTTPException(status_code=400, detail="模型 config 為空")

    print("max_tokens",request.max_tokens)

    # 呼叫 Azure OpenAI API (新版)
    max_retries =1  # 最多重試 3 次
    for attempt in range(max_retries):
        try:
            if provider == "azure":
                from openai import AzureOpenAI
                client = AzureOpenAI(
                    api_key=config["api_key"],
                    api_version="2023-07-01-preview",
                    azure_endpoint=config["endpoint"]
                )
                print("Azure 請求發送中")
                response = client.chat.completions.create(
                    model=config["deployment_name"],
                    messages=prompt_messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    top_p=request.top_p,
                    presence_penalty=request.presence_penalty,
                    frequency_penalty=request.frequency_penalty
                )
                print("Azure 回覆成功")
                assistant_message = response.choices[0].message.content

            elif provider == "gemini":
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=config["api_key"])

                    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
                    print("Gemini 請求發送中")

                    user_prompt = prompt_messages[-1]["content"]
                    print("Gemini Prompt Content:", user_prompt)

                    result = model.generate_content(user_prompt)
                    assistant_message = result.text

                    print("Gemini 回覆成功")

                except Exception as e:
                    print("Gemini 發生錯誤：", str(e))
                    raise HTTPException(status_code=500, detail=f"Gemini API 錯誤：{str(e)}")

            else:
                raise HTTPException(status_code=400, detail="不支援的供應商")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"API 失敗: {str(e)}")
            time.sleep(1)  # 等待 1 秒再重試

    # 儲存對話記錄到資料庫
    user_msg = ChatMessage(talk_id=request.talk_id, sender="user", message=request.user_message)
    assistant_msg = ChatMessage(talk_id=request.talk_id, sender="assistant", message=assistant_message)
    
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    # ✅ 嘗試自動生成記憶（每 10 則對話）
    generate_memory(db, request.talk_id, session.role_id, session.id,5)
    return {
        "talk_id": request.talk_id,
        "user_message_id": user_msg.id,
        "assistant_message_id": assistant_msg.id,
        "assistant_message": assistant_message,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

@router.get("/api/chat/{talk_id}/history", response_model=ChatHistoryResponse)
def get_chat_history(talk_id: int, limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage) \
        .filter(ChatMessage.talk_id == talk_id) \
        .order_by(ChatMessage.id.desc()) \
        .limit(limit).offset(offset).all()
    
    has_more = db.query(ChatMessage).filter(ChatMessage.talk_id == talk_id).count() > (limit + offset)
    
    return {
        "talk_id": talk_id,
        "messages": messages,
        "has_more": has_more
    }

@router.put("/api/chat/message/{message_id}")
def update_message(message_id: int, request: UpdateMessageRequest, db: Session = Depends(get_db)):
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if not request.new_message.strip():
        raise HTTPException(status_code=400, detail="New message content cannot be empty")

    old_message = message.message
    message.message = request.new_message
    message.updated_at = datetime.utcnow()  # 確保 `updated_at` 被更新
    db.commit()
    db.refresh(message)


    return {
        "message_id": message_id,
        "old_message": old_message,
        "new_message": message.message,
        "updated_at": message.updated_at
    }

def generate_memory(db: Session, talk_id: int, role_id: int, session_id: int, message_count: int):
    from tiktoken import encoding_for_model  # 用於 token 計算
    try:
        # 總對話筆數
        total = db.query(ChatMessage).filter(ChatMessage.talk_id == talk_id).count()
        if total % message_count != 0:  # ✅ 每 10 則觸發一次
            print("本次不生成回憶")
            return
        print("組織生成記憶prompt")

        # 抓最近 10 則訊息（新到舊）
        recent = (
            db.query(ChatMessage)
            .filter(ChatMessage.talk_id == talk_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(message_count).all()
        )
        recent = list(reversed(recent))
        print("recent")  # 轉成舊到新

        # 組合對話內容
        context = "\n".join([f"{m.sender}：{m.message}" for m in recent])

        # 設計 Prompt
        summary_prompt = [
            {
                "role": "system",
                "content": "你是小說寫作助手，請根據以下 5 輪對話（共 10 則訊息），整理出一句具體的事件或記憶摘要（不超過 100 字），並加上 1～3 個合適的分類標籤。\n\n格式如下：\n記憶內容：...\n標籤：...\n"
            },
            {
                "role": "user",
                "content": context
            }
        ]

        # 呼叫模型
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=summary_prompt,
            temperature=0.5,
            max_tokens=200
        )
        result = response.choices[0].message.content
        print("模型回覆")
        print(result)

        # 解析回傳內容
        lines = result.strip().splitlines()
        memory_text = ""
        tags = ""
        for line in lines:
            if line.startswith("記憶內容："):
                memory_text = line.replace("記憶內容：", "").strip()
            elif line.startswith("標籤："):
                tags = line.replace("標籤：", "").strip()

        # Token 計算（選擇性）
        enc = encoding_for_model("gpt-4")
        token_count = len(enc.encode(memory_text))

        # 寫入記憶體資料表
        db.add(Memory(
            role_id=role_id,
            session_id=session_id,
            content=memory_text,
            token_count=token_count,
            tags=tags,
            is_active=True,
            selected=False
        ))
        db.commit()
        print("[✅] 自動記憶生成成功")
    except Exception as e:
        print(f"[⚠️] 自動記憶生成失敗：{e}")

@router.delete("/api/chat/message/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()

    return {"message": f"Message {message_id} deleted successfully"}


@router.get("/api/sessions/{session_id}/role", response_model=RoleSchema)
def read_role_by_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    role = get_role_by_session(db, session_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found for session")

    # 加上完整圖片網址
    if role.image:
        base_url = str(request.base_url).rstrip("/")
        role.image = f"{base_url}/{role.image}"

    return role