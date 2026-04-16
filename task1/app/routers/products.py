from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas import ProductCreate, ProductRead
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def get_service(session: AsyncSession = Depends(get_session)) -> ProductService:
    return ProductService(session)


@router.get("", response_model=list[ProductRead])
async def list_products(service: ProductService = Depends(get_service)):
    return await service.list_products()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, service: ProductService = Depends(get_service)):
    return await service.get_product(product_id)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate, service: ProductService = Depends(get_service)
):
    return await service.create_product(payload)
