from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.models import WaitlistEntry
from app.schemas.schemas import WaitlistCreate, WaitlistResponse

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


@router.post("", response_model=WaitlistResponse, status_code=201)
def join_waitlist(payload: WaitlistCreate, db: Session = Depends(get_db)):
    """Add a new email to the HYDRA waitlist."""
    entry = WaitlistEntry(name=payload.name, email=payload.email)
    db.add(entry)
    try:
        db.commit()
        db.refresh(entry)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This email is already on the waitlist.")
    return entry


@router.get("", response_model=list[WaitlistResponse])
def list_waitlist(db: Session = Depends(get_db)):
    """Admin: view all waitlist entries."""
    return db.query(WaitlistEntry).order_by(WaitlistEntry.created_at.desc()).all()
