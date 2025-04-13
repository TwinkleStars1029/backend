from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, schemas, repository, models
from typing import List

router = APIRouter(
    prefix="/api/sessions",
    tags=["sessions"]
)

@router.get("/", response_model=list[schemas.ChatSessionOut])
def read_sessions(db: Session = Depends(database.get_db)):
    return repository.get_sessions(db)

@router.get("/{session_id}", response_model=schemas.ChatSessionOut)
def read_session(session_id: int, db: Session = Depends(database.get_db)):
    session = repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/", response_model=schemas.ChatSessionOut)
def create_session(session: schemas.ChatSessionCreate, db: Session = Depends(database.get_db)):
    return repository.create_session(db, session)

@router.put("/{session_id}", response_model=schemas.ChatSessionOut)
def update_session(session_id: int, session: schemas.ChatSessionUpdate, db: Session = Depends(database.get_db)):
    return repository.update_session(db, session_id, session)

@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(database.get_db)):
    repository.delete_session(db, session_id)
    return {"message": "Session deleted"}

@router.get("/by-role/{role_id}", response_model=List[schemas.ChatSessionOut])
def get_sessions_by_role(role_id: int, db: Session = Depends(database.get_db)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.role_id == role_id).order_by(models.ChatSession.created_at.desc()).all()
    return sessions
