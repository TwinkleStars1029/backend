# routers/events.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database, schemas, repository
from typing import List
import models



router = APIRouter(
    prefix="/api/events",
    tags=["events"]
)

@router.get("/", response_model=list[schemas.EventOut])
def read_events(db: Session = Depends(database.get_db)):
    return repository.get_events(db)

@router.get("/{event_id}", response_model=schemas.EventOut)
def read_event(event_id: int, db: Session = Depends(database.get_db)):
    event = repository.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(database.get_db)):
    return repository.create_event(db, event)

@router.put("/{event_id}", response_model=schemas.EventOut)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(database.get_db)):
    return repository.update_event(db, event_id, event)

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(database.get_db)):
    repository.delete_event(db, event_id)
    return {"message": "Event deleted"}

@router.get("/session/{session_id}", response_model=List[schemas.EventOut])
def get_events_by_session(session_id: int, db: Session = Depends(database.get_db)):
    events = db.query(models.Event).filter(models.Event.session_id == session_id).all()
    return events
