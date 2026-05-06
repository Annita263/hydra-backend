from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.models import OrderStatus


# ---------- Waitlist ----------

class WaitlistCreate(BaseModel):
    name: str
    email: EmailStr


class WaitlistResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Products ----------

class ProductResponse(BaseModel):
    id: int
    name: str
    variant: str
    description: str
    price: float
    stock: int

    class Config:
        from_attributes = True


# ---------- Orders ----------

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str | None = None
    product_id: int
    quantity: int = 1


class OrderResponse(BaseModel):
    id: int
    reference: str
    customer_name: str
    customer_email: str
    quantity: int
    total_amount: float
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Payments ----------

class PaymentInitResponse(BaseModel):
    authorization_url: str   # Redirect user here to pay on Paystack
    access_code: str
    reference: str


class PaymentVerifyResponse(BaseModel):
    status: str
    reference: str
    amount: float
    order_id: int
