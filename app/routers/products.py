from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Product
from app.schemas.schemas import ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """Return all available HYDRA product variants."""
    return db.query(Product).filter(Product.stock > 0).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product
