from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.product import Product


class ProductRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Product]:
        result = await self.session.execute(
            select(Product)
        )

        return list(result.scalars().all())

    async def create(
            self,
            name: str,
            price,
    ) -> Product:
        product = Product(
            name=name,
            price=price
        )

        self.session.add(product)

        await self.session.flush()
        await self.session.refresh(product)

        return product