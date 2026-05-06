from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.models import CartItem, Product, User
from app.utils.security import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

class CartAddRequest(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_variant: str
    price: float
    quantity: int
    subtotal: float

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: float

@router.post("/add", status_code=201)
def add_to_cart(payload: CartAddRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    existing = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.product_id == payload.product_id).first()
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(CartItem(user_id=current_user.id, product_id=payload.product_id, quantity=payload.quantity))
    db.commit()
    return {"message": "Added to cart."}

@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    result = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        result.append(CartItemResponse(id=item.id, product_id=item.product_id, product_name=product.name, product_variant=product.variant, price=product.price, quantity=item.quantity, subtotal=product.price * item.quantity))
    return CartResponse(items=result, total=sum(i.subtotal for i in result))

@router.delete("/remove/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    db.delete(item)
    db.commit()
    return {"message": "Item removed."}

@router.delete("/clear")
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared."}