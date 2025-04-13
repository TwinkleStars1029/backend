from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, repository, database
from typing import List
import models

router = APIRouter(
    prefix="/api/memories",
    tags=["memories"]
)

@router.get("/", response_model=list[schemas.MemoryOut])
def read_memories(db: Session = Depends(database.get_db)):
    return repository.get_memories(db)

@router.get("/{memory_id}", response_model=schemas.MemoryOut)
def read_memory(memory_id: int, db: Session = Depends(database.get_db)):
    memory = repository.get_memory_by_id(db, memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.post("/", response_model=schemas.MemoryOut)
def create_memory(memory: schemas.MemoryCreate, db: Session = Depends(database.get_db)):
    return repository.create_memory(db, memory)

@router.put("/{memory_id}", response_model=schemas.MemoryOut)
def update_memory(memory_id: int, memory: schemas.MemoryUpdate, db: Session = Depends(database.get_db)):
    return repository.update_memory(db, memory_id, memory)

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(database.get_db)):
    repository.delete_memory(db, memory_id)
    return {"message": "Memory deleted"}

@router.get("/session/{session_id}", response_model=List[schemas.MemoryOut])
def get_memory_by_session(session_id: int, db: Session = Depends(database.get_db)):
    events = db.query(models.Memory).filter(models.Memory.session_id == session_id).all()
    return events
