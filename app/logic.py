from app.models import Order, OrderLine
from app.storage import JsonStore, STORE_LOCK

TAX_RATE = 0.05


class CanteenService:
    def __init__(self, menu: JsonStore, orders: JsonStore):
        self.menu_store, self.order_store = menu, orders

    def menu(self):
        return self.menu_store.read()

    def create_menu_item(self, payload):
        with STORE_LOCK:
            records = self.menu_store.read()
            next_id = max((x["id"] for x in records), default=0) + 1
            item = {"id": next_id, **payload.model_dump()}
            records.append(item)
            self.menu_store.write(records)
            return item

    def update_menu_item(self, item_id, payload):
        with STORE_LOCK:
            records = self.menu_store.read()
            for i, item in enumerate(records):
                if item["id"] == item_id:
                    records[i] = {"id": item_id, **payload.model_dump()}
                    self.menu_store.write(records)
                    return records[i]
        return None

    def delete_menu_item(self, item_id):
        with STORE_LOCK:
            records = self.menu_store.read()
            remaining = [x for x in records if x["id"] != item_id]
            if len(remaining) == len(records):
                return False
            self.menu_store.write(remaining)
            return True

    def orders(self):
        return self.order_store.read()

    def create_order(self, payload):
        with STORE_LOCK:
            menu = {x["id"]: x for x in self.menu_store.read()}
            lines, subtotal = [], 0.0
            for requested in payload.lines:
                item = menu.get(requested.item_id)
                if item is None or not item["available"]:
                    return None
                amount = round(item["price"] * requested.quantity, 2)
                subtotal += amount
                lines.append(OrderLine(item_id=item["id"], name=item["name"], unit_price=item["price"], quantity=requested.quantity, line_total=amount))
            subtotal = round(subtotal, 2)
            tax = round(subtotal * TAX_RATE, 2)
            records = self.order_store.read()
            order = Order(id=max((x["id"] for x in records), default=0) + 1, lines=lines, subtotal=subtotal, tax=tax, total=round(subtotal + tax, 2))
            records.append(order.model_dump())
            self.order_store.write(records)
            return order

    def get_order(self, order_id):
        return next((x for x in self.order_store.read() if x["id"] == order_id), None)

    def update_status(self, order_id, status):
        with STORE_LOCK:
            records = self.order_store.read()
            for i, order in enumerate(records):
                if order["id"] == order_id:
                    records[i] = {**order, "status": status}
                    self.order_store.write(records)
                    return records[i]
        return None
