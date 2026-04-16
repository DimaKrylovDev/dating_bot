from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas import CustomerCreate, CustomerEmailUpdate, CustomerRead
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


def get_service(session: AsyncSession = Depends(get_session)) -> CustomerService:
    return CustomerService(session)


@router.get("", response_model=list[CustomerRead])
async def list_customers(service: CustomerService = Depends(get_service)):
    return await service.list_customers()


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: int, service: CustomerService = Depends(get_service)):
    return await service.get_customer(customer_id)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate, service: CustomerService = Depends(get_service)
):
    return await service.create_customer(payload)


@router.patch("/{customer_id}/email", response_model=CustomerRead)
async def update_email(
    customer_id: int,
    payload: CustomerEmailUpdate,
    service: CustomerService = Depends(get_service),
):
    return await service.update_email(customer_id, payload.email)
