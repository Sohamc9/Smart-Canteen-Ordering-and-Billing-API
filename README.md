# Smart Canteen Ordering and Billing API

A teaching prototype for a campus canteen. It stores menu items and orders as JSON files. It does not connect to a payment processor and a completed order does not mean payment was made.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive Swagger UI or <http://127.0.0.1:8000/redoc>. Data is stored in `data/menu.json` and `data/orders.json`. Set `CANTEEN_DATA_DIR` to use another folder.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/menu` | List menu items |
| POST | `/api/menu` | Add item (201) |
| PUT | `/api/menu/{item_id}` | Replace item fields |
| DELETE | `/api/menu/{item_id}` | Remove item (204) |
| POST | `/api/orders` | Create order and bill (201) |
| GET | `/api/orders/{order_id}` | Retrieve order/bill |
| PATCH | `/api/orders/{order_id}/status` | Set pending/preparing/ready/completed/cancelled |
| GET | `/health` | Basic health response |

Invalid request fields return 422; missing IDs return 404. Order creation returns 201 when the order resource is created. It is not a payment confirmation.

## Billing rule

Subtotal is the sum of each menu price times quantity, rounded to two decimal places. Tax is a flat **5% of subtotal**, rounded to two decimal places. There is no discount. Total is subtotal plus tax. Currency is not encoded by the API; prices in the sample are illustrative. No real payment is taken.

## Route demonstration

With the server running, use Swagger UI at `/docs`, or run these HTTP requests:

```bash
curl http://127.0.0.1:8000/api/menu
curl -X POST http://127.0.0.1:8000/api/orders \\
  -H 'Content-Type: application/json' \\
  -d '{"lines":[{"item_id":1,"quantity":2},{"item_id":2,"quantity":1}]}'
curl http://127.0.0.1:8000/api/orders/1
curl -X PATCH http://127.0.0.1:8000/api/orders/1/status \\
  -H 'Content-Type: application/json' \\
  -d '{"status":"ready"}'
```

To demonstrate persistence, create an order, stop Uvicorn with Ctrl+C, start it again using the same command, then retrieve the same `/api/orders/{id}`. The order is read from `data/orders.json` after restart.

## Tests

```bash
pytest -q
```

The tests use FastAPI's `TestClient`, which exercises the app in-process without starting a network server. They cover route success, invalid input, missing IDs and JSON readback through a fresh store instance.

## Who provides what

FastAPI provides routing, dependency/request handling, OpenAPI generation, interactive docs and HTTP response handling. Pydantic provides request/response model validation and JSON-compatible model serialization. Uvicorn runs the ASGI app. `pytest` and FastAPI's re-export of Starlette's `TestClient` support tests. This project authors the models, routes, canteen rules, JSON storage layer, file layout, tests and this documentation.

## JSON persistence limitations

- A process-wide lock protects each read-modify-write operation from other threads in this one Python process. Separate worker processes or multiple app instances do not share that lock and can race, duplicate IDs, or overwrite one another's changes.
- Atomic file replacement protects readers from observing a partially written target file, but it does not provide a multi-file transaction, durable database journal, or conflict detection.
- A crash, disk-full condition, filesystem issue or manual edit can leave data unavailable or inconsistent; JSON files have no built-in backups, recovery, indexing, access controls, or schema migration.
- Each update rewrites the whole file, so larger datasets make writes slower and increases lost-update risk when writers are not coordinated.

For a classroom demo, run one process and keep backups. Use a database with transactions and concurrency control for shared or production use.

## AI Verification Log

Checked against official documentation and package references on 2026-11-24. For claims about nonexistent names, lack of a match in official documentation/package references is evidence that they are not standard APIs, not a proof that nobody has ever published a similarly named private or unrelated project.

| Tutorial claim | Finding and correction |
|---|---|
| `@app.autosave_json()` is supported by FastAPI | No such decorator appears in FastAPI's documented API. This project writes JSON in its own `JsonStore` storage module. |
| Pydantic includes `PydanticMagicInvoice` | No such built-in model appears in Pydantic's documented API. This project defines its own request and response models in `app/models.py`. |
| HTTP 209 “Order Persisted” is standard for create | HTTP 209 is unassigned in the IANA HTTP status code registry, so it is not a standard create status. Use HTTP 201 Created for a newly created resource. 201 says the resource was created; it says nothing about payment. |
| `response_model_autobill=True` calculates bills | Not a documented FastAPI option. `response_model` validates/serializes/documents response shape; this project's service code calculates subtotal, tax and total. |
| Pydantic has `@computed_total` | Not a documented Pydantic decorator. Pydantic documents `@computed_field` for computed model fields; this project calculates totals explicitly in business logic. |
| `fastapi-jsonvault` provides transaction-safe concurrent JSON writes | No verifiable authoritative package documentation was found for this claim. The app uses standard-library temp-file + `os.replace` writes, which are atomic for replacing a file on the same filesystem, but not a multi-process transaction or concurrency solution. |
| HTTP 201 means payment completed | False. HTTP 201 indicates resource creation. This API performs no payment processing. |
| `TestClient` tests routes without a server | True. FastAPI documents `fastapi.testclient.TestClient`; tests here run in-process. |

### References

- FastAPI response status codes: <https://fastapi.tiangolo.com/tutorial/response-status-code/>
- FastAPI response models: <https://fastapi.tiangolo.com/tutorial/response-model/>
- FastAPI testing / TestClient: <https://fastapi.tiangolo.com/tutorial/testing/>
- Pydantic computed fields: <https://pydantic.dev/docs/validation/latest/concepts/fields/#the-computed_field-decorator>
- IANA HTTP status code registry: <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>
- PyPI package lookup for the alleged package: <https://pypi.org/project/fastapi-jsonvault/>
