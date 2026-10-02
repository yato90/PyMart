from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.category import Category
from app.database.models.product import Product

class CategoryRepository:

    def __init__(self, session: AsyncSession):
            self.session = session

    async def get_by_id(self, category_id:int) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(
            select(Category).order_by(Category.id)
        )

        return list(result.scalars().all())

    async def create(self, name: str) -> Category:
        category = Category(name=name)

        self.session.add(category)

        await self.session.flush()
        await self.session.refresh(category)

        return category

    async def has_products(self, category_id: int) -> bool:
        result = await self.session.execute(
            select(
                exists().where(
                    Product.category_id == category_id
                )
            )
        )

        return bool(result.scalar())

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)