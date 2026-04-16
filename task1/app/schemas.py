from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Customer ----------
class CustomerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class CustomerCreate(CustomerBase):
    pass


class CustomerEmailUpdate(BaseModel):
    email: EmailStr


class CustomerRead(CustomerBase):
    customer_id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Product ----------
class ProductBase(BaseModel):
    product_name: str = Field(min_length=1, max_length=255)
    price: Decimal = Field(gt=0, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    product_id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Order ----------
class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemRead(BaseModel):
    order_item_id: int
    product_id: int
    quantity: int
    subtotal: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    order_id: int
    customer_id: int
    order_date: datetime
    total_amount: Decimal
    items: list[OrderItemRead]
    model_config = ConfigDict(from_attributes=True)
