from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_name(self, name: str) -> Product | None:
        stmt = select(Product).where(Product.product_name == name)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_all(self) -> list[Product]:
        stmt = select(Product).order_by(Product.product_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def add(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product
