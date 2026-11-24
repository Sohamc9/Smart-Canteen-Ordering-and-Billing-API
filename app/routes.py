from fastapi import APIRouter, HTTPException, Response, status
from app.models import MenuItem, MenuItemCreate, Order, OrderCreate, OrderStatusUpdate


def build_router(service):
    router = APIRouter()

    @router.get("/menu", response_model=list[MenuItem])
    def list_menu():
        return service.menu()

    @router.post("/menu", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
    def add_menu_item(payload: MenuItemCreate):
        return service.create_menu_item(payload)

    @router.put("/menu/{item_id}", response_model=MenuItem)
    def edit_menu_item(item_id: int, payload: MenuItemCreate):
        item = service.update_menu_item(item_id, payload)
        if item is None:
            raise HTTPException(404, "Menu item not found")
        return item

    @router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def remove_menu_item(item_id: int):
        if not service.delete_menu_item(item_id):
            raise HTTPException(404, "Menu item not found")
        return Response(status_code=204)

    @router.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
    def create_order(payload: OrderCreate):
        order = service.create_order(payload)
        if order is None:
            raise HTTPException(422, "An item is missing or unavailable")
        return order

    @router.get("/orders/{order_id}", response_model=Order)
    def read_order(order_id: int):
        order = service.get_order(order_id)
        if order is None:
            raise HTTPException(404, "Order not found")
        return order

    @router.patch("/orders/{order_id}/status", response_model=Order)
    def update_order_status(order_id: int, payload: OrderStatusUpdate):
        order = service.update_status(order_id, payload.status)
        if order is None:
            raise HTTPException(404, "Order not found")
        return order

    return router
