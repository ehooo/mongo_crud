from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    IntegerError,
    validator,
)


class ErrorMessage(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "Error message"},
        }


class CategoryModel(BaseModel):
    category_id: int = Field()
    name: str = Field()
    parent_id: Optional[int] = Field()

    class Config:
        schema_extra = {
            "subcategory": {
                "category_id": 2,
                "name": "Men",
                "parent_id": 1
            },
            "category": {
                "category_id": 1,
                "name": "Clothes",
            }
        }


class SingleCategoryModel(BaseModel):
    name: str = Field()
    parent_id: str = Field()

    @validator("parent_id")
    def check_int(cls, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise IntegerError()

    class Config:
        schema_extra = {
            "subcategory": {
                "name": "Men",
                "parent_id": 1
            },
            "category": {
                "name": "Clothes",
            }
        }
