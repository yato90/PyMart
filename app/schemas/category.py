from pydantic import BaseModel


class CreateCategoryRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str