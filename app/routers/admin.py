from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.models import Order, Product, User, WaitlistEntry, OrderStatus

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─── Schemas ───────────────────────────────────────────────────────────────

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

class TickerMessage(BaseModel):
    message: str

class HeroUpdate(BaseModel):
    headline: Optional[str] = None
    subheadline: Optional[str] = None
    description: Optional[str] = None
    cta_text: Optional[str] = None

class SettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    contact_email: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None


# ─── In-memory store for hero + ticker + settings ──────────────────────────

_hero = {
    "headline": "REPLENISH WHAT YOU LOSE.",
    "subheadline": "PERFORM WHAT MATTERS.",
    "description": "HYDRA is a clean-label electrolyte drink designed for daily hydration in hot African climates. No sugar overload. No artificial additives. Just what your body needs.",
    "cta_text": "Shop Now",
}

_ticker_messages = [
    {"id": 1, "message": "Human hydration — low sugar"},
    {"id": 2, "message": "Stay hydrated"},
    {"id": 3, "message": "Daily hydration"},
    {"id": 4, "message": "No artificial additives"},
    {"id": 5, "message": "Low sugar"},
    {"id": 6, "message": "Real electrolytes"},
    {"id": 7, "message": "Documentation available — visit our website"},
]

_settings = {
    "site_name": "HYDRA",
    "contact_email": "hello@drinkhydra.com",
    "instagram": "@drinkhydra",
    "twitter": "@drinkhydra",
}

_ticker_counter = {"count": len(_ticker_messages)}


# ─── Overview ──────────────────────────────────────────────────────────────

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    paid_orders = db.query(Order).filter(Order.status == OrderStatus.PAID).count()
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status == OrderStatus.PAID).scalar() or 0
    total_customers = db.query(User).count()
    total_waitlist = db.query(WaitlistEntry).count()
    total_products = db.query(Product).count()
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()

    return {
        "stats": {
            "total_products": total_products,
            "total_orders": total_orders,
            "paid_orders": paid_orders,
            "total_revenue_ngn": round(total_revenue, 2),
            "total_customers": total_customers,
            "waitlist_signups": total_waitlist,
            "today": datetime.utcnow().strftime("%A, %d %B %Y"),
        },
        "recent_orders": [
            {
                "id": o.id,
                "reference": o.reference,
                "customer_name": o.customer_name,
                "customer_email": o.customer_email,
                "total_amount": o.total_amount,
                "status": o.status,
                "created_at": o.created_at,
            } for o in recent_orders
        ]
    }


# ─── Products ──────────────────────────────────────────────────────────────

@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if payload.name is not None:
        product.name = payload.name
    if payload.description is not None:
        product.description = payload.description
    if payload.price is not None:
        product.price = payload.price
    if payload.stock is not None:
        product.stock = payload.stock
    db.commit()
    db.refresh(product)
    return product


# ─── Hero Section ──────────────────────────────────────────────────────────

@router.get("/hero")
def get_hero():
    return _hero


@router.put("/hero")
def update_hero(payload: HeroUpdate):
    if payload.headline is not None:
        _hero["headline"] = payload.headline
    if payload.subheadline is not None:
        _hero["subheadline"] = payload.subheadline
    if payload.description is not None:
        _hero["description"] = payload.description
    if payload.cta_text is not None:
        _hero["cta_text"] = payload.cta_text
    return _hero


# ─── Ticker Strip ──────────────────────────────────────────────────────────

@router.get("/ticker")
def get_ticker():
    return {"messages": _ticker_messages}


@router.post("/ticker", status_code=201)
def add_ticker_message(payload: TickerMessage):
    _ticker_counter["count"] += 1
    new_msg = {"id": _ticker_counter["count"], "message": payload.message}
    _ticker_messages.append(new_msg)
    return new_msg


@router.delete("/ticker/{message_id}")
def delete_ticker_message(message_id: int):
    global _ticker_messages
    original_len = len(_ticker_messages)
    _ticker_messages = [m for m in _ticker_messages if m["id"] != message_id]
    if len(_ticker_messages) == original_len:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"message": "Deleted successfully."}


# ─── Settings ──────────────────────────────────────────────────────────────

@router.get("/settings")
def get_settings():
    return _settings


@router.put("/settings")
def update_settings(payload: SettingsUpdate):
    if payload.site_name is not None:
        _settings["site_name"] = payload.site_name
    if payload.contact_email is not None:
        _settings["contact_email"] = payload.contact_email
    if payload.instagram is not None:
        _settings["instagram"] = payload.instagram
    if payload.twitter is not None:
        _settings["twitter"] = payload.twitter
    return _settings


# ─── Orders ────────────────────────────────────────────────────────────────

@router.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "reference": o.reference,
            "customer_name": o.customer_name,
            "customer_email": o.customer_email,
            "quantity": o.quantity,
            "total_amount": o.total_amount,
            "status": o.status,
            "created_at": o.created_at,
            "paid_at": o.paid_at,
        } for o in orders
    ]


# ─── Waitlist ──────────────────────────────────────────────────────────────

@router.get("/waitlist")
def list_waitlist(db: Session = Depends(get_db)):
    return db.query(WaitlistEntry).order_by(WaitlistEntry.created_at.desc()).all()