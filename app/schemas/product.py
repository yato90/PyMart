from decimal import Decimal
from pydantic import BaseModel

class CreateProductRequest(BaseModel):
    name: str
    price: Decimal
    category_id: int

class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    category_id: int

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    next_cursor: str | None