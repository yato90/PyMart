from datetime import datetime

from sqlalchemy import select, and_, or_, tuple_
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

    async def get_all(
                self,
                limit: int,
                cursor_created_at: datetime | None = None,
                cursor_id: int | None = None,
        ) -> list[Product]:
        query = (
            select(Product)
            .order_by(
                Product.created_at.desc(),
                Product.id.desc(),
            )
            .limit(limit)
        )

        if cursor_created_at is not None and cursor_id is not None:
            query = query.where(
                tuple_(
                    Product.created_at,
                    Product.id,
                )
                < tuple_(
                    cursor_created_at,
                    cursor_id,
                )
            )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_by_category_id(
                self,
                category_id: int,
                limit: int,
                cursor_created_at: datetime | None = None,
                cursor_id: int | None = None,
        ) -> list[Product]:
            query = (
                select(Product)
                .where(Product.category_id == category_id)
                .order_by(
                    Product.created_at.desc(),
                    Product.id.desc()
                )
                .limit(limit)
            )

            if cursor_created_at is not None and cursor_id is not None:
                query = query.where(
                    tuple_(
                        Product.created_at,
                        Product.id,
                    )
                    < tuple_(
                        cursor_created_at,
                        cursor_id,
                    )
                )
                # query = query.where(
                #     or_(
                #         Product.created_at < cursor_created_at,
                #         and_(
                #             Product.created_at == cursor_created_at,
                #             Product.id < cursor_id,
                #         ),
                #     )
                # )

            result = await self.session.execute(query)

            return list(result.scalars().all())

    async def create(
            self,
            name: str,
            price,
            category_id: int
    ) -> Product:
        product = Product(
            name=name,
            price=price,
            category_id=category_id
        )

        self.session.add(product)

        await self.session.flush()
        await self.session.refresh(product)

        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)