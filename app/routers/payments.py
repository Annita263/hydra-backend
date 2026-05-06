from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import httpx

from app.database import get_db
from app.models.models import Order, OrderStatus
from app.schemas.schemas import PaymentInitResponse, PaymentVerifyResponse
from app.config import settings
from app.utils.email import send_order_confirmation

router = APIRouter(prefix="/payments", tags=["Payments"])

PAYSTACK_BASE = "https://api.paystack.co"
HEADERS = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}


@router.post("/initiate/{order_id}", response_model=PaymentInitResponse)
def initiate_payment(order_id: int, db: Session = Depends(get_db)):
    """
    Kick off a Paystack payment for an order.
    Returns a URL to redirect the customer to.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    if order.status == OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="Order is already paid.")

    # Paystack expects amount in kobo (NGN * 100)
    amount_kobo = int(order.total_amount * 100)

    payload = {
        "email": order.customer_email,
        "amount": amount_kobo,
        "reference": order.reference,
        "callback_url": f"{settings.BASE_URL}/payments/verify/{order.reference}",
        "metadata": {
            "order_id": order.id,
            "customer_name": order.customer_name,
        },
    }

    response = httpx.post(f"{PAYSTACK_BASE}/transaction/initialize", json=payload, headers=HEADERS)
    data = response.json()

    if not data.get("status"):
        raise HTTPException(status_code=502, detail=f"Paystack error: {data.get('message')}")

    return PaymentInitResponse(
        authorization_url=data["data"]["authorization_url"],
        access_code=data["data"]["access_code"],
        reference=data["data"]["reference"],
    )


@router.get("/verify/{reference}", response_model=PaymentVerifyResponse)
def verify_payment(reference: str, db: Session = Depends(get_db)):
    """
    Called after the customer returns from Paystack.
    Verifies with Paystack and marks the order as paid.
    """
    order = db.query(Order).filter(Order.reference == reference).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    response = httpx.get(f"{PAYSTACK_BASE}/transaction/verify/{reference}", headers=HEADERS)
    data = response.json()

    if not data.get("status") or data["data"]["status"] != "success":
        raise HTTPException(status_code=400, detail="Payment not successful.")

    # Mark order as paid
    order.status = OrderStatus.PAID
    order.paid_at = datetime.utcnow()
    order.paystack_reference = data["data"]["reference"]
    db.commit()
    db.refresh(order)

    # Send confirmation email (non-blocking — if it fails, order is still marked paid)
    try:
        send_order_confirmation(order)
    except Exception:
        pass

    return PaymentVerifyResponse(
        status="success",
        reference=reference,
        amount=data["data"]["amount"] / 100,
        order_id=order.id,
    )


@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Paystack calls this endpoint directly after a successful payment.
    This is the reliable fallback if the user closes the browser early.
    """
    payload = await request.json()
    event = payload.get("event")

    if event == "charge.success":
        reference = payload["data"]["reference"]
        order = db.query(Order).filter(Order.reference == reference).first()

        if order and order.status != OrderStatus.PAID:
            order.status = OrderStatus.PAID
            order.paid_at = datetime.utcnow()
            order.paystack_reference = reference
            db.commit()
            db.refresh(order)

            try:
                send_order_confirmation(order)
            except Exception:
                pass

    return {"status": "ok"}
