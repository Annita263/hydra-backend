import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Order, Product
from app.schemas.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order. Returns the order with a reference for payment."""
    # Check the product exists and has stock
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available.")

    total = product.price * payload.quantity
    reference = f"HYDRA-{uuid.uuid4().hex[:10].upper()}"

    order = Order(
        reference=reference,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone,
        product_id=payload.product_id,
        quantity=payload.quantity,
        total_amount=total,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    """Admin: view all orders."""
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order
