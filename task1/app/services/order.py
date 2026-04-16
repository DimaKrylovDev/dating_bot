from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models import Order, OrderItem
from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository
from app.repositories.product import ProductRepository
from app.schemas import OrderCreate


class OrderService:
    """Сценарий 1 реализован в `place_order`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.orders = OrderRepository(session)
        self.products = ProductRepository(session)
        self.customers = CustomerRepository(session)

    async def get_order(self, order_id: int) -> Order:
        order = await self.orders.get(order_id)
        if order is None:
            raise NotFoundError(f"Заказ {order_id} не найден")
        return order

    async def list_for_customer(self, customer_id: int) -> list[Order]:
        return await self.orders.list_for_customer(customer_id)

    async def place_order(self, payload: OrderCreate) -> Order:
        async with self.session.begin():
            customer = await self.customers.get(payload.customer_id)
            if customer is None:
                raise NotFoundError(f"Клиент {payload.customer_id} не найден")

            order = Order(customer_id=customer.customer_id, total_amount=Decimal("0"))
            await self.orders.add(order)

            total = Decimal("0")
            for line in payload.items:
                product = await self.products.get(line.product_id)

                if product is None:
                    raise NotFoundError(f"Продукт {line.product_id} не найден")

                subtotal = (product.price * line.quantity).quantize(Decimal("0.01"))
                await self.orders.add_item(
                    OrderItem(
                        order_id=order.order_id,
                        product_id=product.product_id,
                        quantity=line.quantity,
                        subtotal=subtotal,
                    )
                )
                total += subtotal

            order.total_amount = total
            await self.session.flush()

        return await self.orders.get(order.order_id)
