from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models import Product
from app.repositories.product import ProductRepository
from app.schemas import ProductCreate


class ProductService:
    """Сценарий 3 реализован в `create_product`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.products = ProductRepository(session)

    async def list_products(self) -> list[Product]:
        return await self.products.list_all()

    async def get_product(self, product_id: int) -> Product:
        product = await self.products.get(product_id)
        if product is None:
            raise NotFoundError(f"Продукт {product_id} не найден")
        return product

    async def create_product(self, payload: ProductCreate) -> Product:
        async with self.session.begin():
            product = Product(**payload.model_dump())
            try:
                await self.products.add(product)
            except IntegrityError as exc:
                raise ConflictError("Продукт с таким именем уже существует") from exc
        return product
