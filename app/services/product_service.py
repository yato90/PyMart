from decimal import Decimal
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import CreateProductRequest, ProductResponse


class ProductService:

    def __init__(self, session: AsyncSession):
        self.repository = ProductRepository(session)
        self.category_repository = CategoryRepository(session)

    async def get_products(self) -> list[ProductResponse]:
        products = await self.repository.get_all()

        return [
            ProductResponse(
                id=product.id,
                name=product.name,
                price=product.price,
                category_id=product.category_id
            )
            for product in products
        ]

    async def get_product(self, product_id: int) -> ProductResponse | None:
        product = await self.repository.get_by_id(product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        
        return ProductResponse(
            id= product.id,
            name= product.name,
            price= product.price,
            category_id= product.category_id
        )
    
    async def create_product(
        self, 
        product_data:CreateProductRequest
    ) -> ProductResponse:

        category = await self.category_repository.get_by_id(
            product_data.category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        product = await self.repository.create(
            name=product_data.name,
            price=product_data.price,
            category_id=product_data.category_id
        )

        await self.repository.session.commit()
        
        return ProductResponse(
            id= product.id,
            name= product.name,
            price= product.price,
            category_id=product.category_id
        )
    