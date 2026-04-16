from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, customer_id: int) -> Customer | None:
        return await self.session.get(Customer, customer_id)

    async def get_by_email(self, email: str) -> Customer | None:
        stmt = select(Customer).where(Customer.email == email)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_all(self) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.customer_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def add(self, customer: Customer) -> Customer:
        self.session.add(customer)
        await self.session.flush()
        return customer

    async def update_email(self, customer: Customer, email: str) -> Customer:
        customer.email = email
        await self.session.flush()
        return customer
