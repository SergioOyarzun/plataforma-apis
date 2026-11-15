from pydantic import BaseModel, ConfigDict, Field


class ProductoIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    precio: int = Field(ge=0, description="Precio en pesos chilenos")
    stock: int = Field(default=0, ge=0)


class Producto(ProductoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int