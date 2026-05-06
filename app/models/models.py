from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="user")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product")


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    variant: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=100)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    customer_email: Mapped[str] = mapped_column(String(255))
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    total_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )
    paystack_reference: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="orders")
    user: Mapped["User"] = relationship("User", back_populates="orders")