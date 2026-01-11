<<<<<<< HEAD
from pydantic import BaseModel, Field
from typing import List, Literal


class MenuItem(BaseModel):
    food_id: int = Field(..., description="ID bahan makanan")
    gram: float = Field(
        default=100,
        gt=0,
        description="Berat makanan dalam gram (default 100g)"
    )


class UserInput(BaseModel):
    age: int = Field(
        ...,
        ge=3,
        le=18,
        description="Usia anak (3–18 tahun)"
    )
    gender: Literal["male", "female"] = Field(
        ...,
        description="Jenis kelamin"
    )
    menu: List[MenuItem]
=======
from pydantic import BaseModel, Field
from typing import List, Literal


class MenuItem(BaseModel):
    food_id: int = Field(..., description="ID bahan makanan")
    gram: float = Field(
        default=100,
        gt=0,
        description="Berat makanan dalam gram (default 100g)"
    )


class UserInput(BaseModel):
    age: int = Field(
        ...,
        ge=3,
        le=18,
        description="Usia anak (3–18 tahun)"
    )
    gender: Literal["male", "female"] = Field(
        ...,
        description="Jenis kelamin"
    )
    menu: List[MenuItem]
>>>>>>> 2973111988d9054ce4d217ed6dc3b0b73b6372ba
