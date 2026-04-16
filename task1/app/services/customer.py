from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models import Customer
from app.repositories.customer import CustomerRepository
from app.schemas import CustomerCreate


class CustomerService:
    """Сценарий 2 реализован в `update_email`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.customers = CustomerRepository(session)

    async def list_customers(self) -> list[Customer]:
        return await self.customers.list_all()

    async def get_customer(self, customer_id: int) -> Customer:
        customer = await self.customers.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Клиент {customer_id} не найден")
        return customer

    async def create_customer(self, payload: CustomerCreate) -> Customer:
        async with self.session.begin():
            customer = Customer(**payload.model_dump())
            try:
                await self.customers.add(customer)
            except IntegrityError as exc:
                raise ConflictError("Email уже используется") from exc
        return customer

    async def update_email(self, customer_id: int, new_email: str) -> Customer:
        async with self.session.begin():
            customer = await self.customers.get(customer_id)
            if customer is None:
                raise NotFoundError(f"Клиент {customer_id} не найден")

            if customer.email == new_email:
                return customer

            try:
                await self.customers.update_email(customer, new_email)
            except IntegrityError as exc:
                raise ConflictError("Email уже используется другим клиентом") from exc
        return customer
