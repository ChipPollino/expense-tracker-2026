from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100) #None не имеет смысла


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)