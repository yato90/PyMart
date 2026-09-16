from decimal import Decimal
from pydantic import BaseModel

class CreateProductRequest(BaseModel):
    name: str
    price: Decimal

class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal