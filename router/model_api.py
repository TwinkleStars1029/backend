from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, repository
from database import get_db
from router.auth import get_current_user

router = APIRouter(prefix="/api/model-apis", tags=["模型 API 金鑰管理"])

# ✅ 簡易清單：GET /api/model-apis/simple-list
@router.get("/simple-list")
def get_user_model_apis(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    model_apis = db.query(models.ModelAPI).filter(models.ModelAPI.user_id == current_user.id).all()
    return [{"id": m.id, "name": m.name} for m in model_apis]

# ✅ 建立新資料：POST /api/model-apis
@router.post("", response_model=schemas.ModelAPIOut)
def create_model_api(data: schemas.ModelAPICreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return repository.create_model_api(db, user.id, data)

# ✅ 取得所有資料：GET /api/model-apis
@router.get("", response_model=list[schemas.ModelAPIOut])
def list_model_apis(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return repository.get_model_apis_by_user(db, user.id)

# ✅ 測試金鑰：POST /api/model-apis/{id}/test
@router.post("/{id:int}/test")
def test_model_api(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    print(f"正在測試 model_api id = {id}, 使用者 = {current_user.id}")
    api_key = db.query(models.ModelAPI).filter(models.ModelAPI.id == id, models.ModelAPI.user_id == current_user.id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="金鑰不存在")

    try:
        if api_key.provider == "azure":
            from openai import AzureOpenAI
            config = api_key.config
            client = AzureOpenAI(
                api_key=config["api_key"],
                api_version="2023-07-01-preview",
                azure_endpoint=config["endpoint"]
            )
            _ = client.chat.completions.create(
                model=config["deployment_name"],
                messages=[{"role": "user", "content": "hello"}]
            )
        elif api_key.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key.config["api_key"])
            model = genai.GenerativeModel("gemini-2.0-flash")
            _ = model.generate_content("hello")
        else:
            raise HTTPException(status_code=400, detail="不支援的供應商")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"測試失敗：{str(e)}")

# ✅ 查詢單一資料：GET /api/model-apis/{id}
@router.get("/{api_id:int}", response_model=schemas.ModelAPIOut)
def get_model_api(api_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    api = db.query(models.ModelAPI).filter_by(id=api_id, user_id=user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="找不到金鑰")
    return api

# ✅ 修改單一資料：PUT /api/model-apis/{id}
@router.put("/{api_id:int}", response_model=schemas.ModelAPIOut)
def update_model_api(api_id: int, data: schemas.ModelAPIUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    api = db.query(models.ModelAPI).filter_by(id=api_id, user_id=user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="找不到金鑰")
    return repository.update_model_api(db, api_id, data)

# ✅ 刪除單一資料：DELETE /api/model-apis/{id}
@router.delete("/{api_id:int}")
def delete_model_api(api_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    api = db.query(models.ModelAPI).filter_by(id=api_id, user_id=user.id).first()
    if not api:
        raise HTTPException(status_code=404, detail="找不到金鑰")
    db.delete(api)
    db.commit()
    return {"message": "已刪除"}
