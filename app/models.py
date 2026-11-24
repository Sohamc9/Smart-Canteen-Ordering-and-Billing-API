from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False)
    available: bool = True


class MenuItem(MenuItemCreate):
    id: int


class OrderLineInput(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    lines: list[OrderLineInput] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|preparing|ready|completed|cancelled)$")


class OrderLine(BaseModel):
    item_id: int
    name: str
    unit_price: float
    quantity: int
    line_total: float


class Order(BaseModel):
    id: int
    lines: list[OrderLine]
    subtotal: float
    tax: float
    total: float
    status: str = "pending"
