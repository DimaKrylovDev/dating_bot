from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas import OrderCreate, OrderRead
from app.services.order import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def get_service(session: AsyncSession = Depends(get_session)) -> OrderService:
    return OrderService(session)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def place_order(payload: OrderCreate, service: OrderService = Depends(get_service)):
    return await service.place_order(payload)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, service: OrderService = Depends(get_service)):
    return await service.get_order(order_id)


@router.get("/customer/{customer_id}", response_model=list[OrderRead])
async def list_for_customer(
    customer_id: int, service: OrderService = Depends(get_service)
):
    return await service.list_for_customer(customer_id)
