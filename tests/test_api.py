import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_menu_order_bill_and_status(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.DATA_DIR", tmp_path)
    # Use temporary stores by swapping the router service's stores.
    from app.main import service
    service.menu_store.path = tmp_path / "menu.json"
    service.order_store.path = tmp_path / "orders.json"
    service.menu_store.write([{"id": 1, "name": "Tea", "price": 20.0, "available": True}])
    service.order_store.write([])
    created = client.post("/api/orders", json={"lines": [{"item_id": 1, "quantity": 2}]})
    assert created.status_code == 201
    assert created.json()["subtotal"] == 40.0
    assert created.json()["tax"] == 2.0
    assert created.json()["total"] == 42.0
    assert client.patch("/api/orders/1/status", json={"status": "ready"}).json()["status"] == "ready"
    assert json.loads((tmp_path / "orders.json").read_text())[0]["id"] == 1


def test_menu_crud_and_missing_ids(tmp_path):
    from app.main import service
    service.menu_store.path = tmp_path / "menu.json"
    service.order_store.path = tmp_path / "orders.json"
    service.menu_store.write([])
    assert client.put("/api/menu/999", json={"name": "X", "price": 1}).status_code == 404
    item = client.post("/api/menu", json={"name": "Idli", "price": 30}).json()
    assert item["id"] == 1
    assert client.put("/api/menu/1", json={"name": "Idli", "price": 35}).json()["price"] == 35
    assert client.delete("/api/menu/1").status_code == 204


def test_invalid_input_and_missing_order(tmp_path):
    from app.main import service
    service.menu_store.path = tmp_path / "menu.json"
    service.order_store.path = tmp_path / "orders.json"
    service.menu_store.write([{"id": 1, "name": "Tea", "price": 20.0, "available": True}])
    service.order_store.write([])
    assert client.post("/api/menu", json={"name": "Bad", "price": -1}).status_code == 422
    assert client.post("/api/orders", json={"lines": [{"item_id": 1, "quantity": -1}]}).status_code == 422
    assert client.get("/api/orders/5").status_code == 404


def test_json_store_survives_new_store_instance(tmp_path):
    from app.storage import JsonStore
    path = tmp_path / "orders.json"
    JsonStore(path, []).write([{"id": 7, "total": 52.5}])
    assert JsonStore(path, []).read() == [{"id": 7, "total": 52.5}]
