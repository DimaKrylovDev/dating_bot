from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_id == order_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_for_customer(self, customer_id: int) -> list[Order]:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.customer_id == customer_id)
            .order_by(Order.order_id.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.flush()
        return order

    async def add_item(self, item: OrderItem) -> OrderItem:
        self.session.add(item)
        return item
