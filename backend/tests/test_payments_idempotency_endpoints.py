from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import payments
from app.middleware.idempotency import IdempotencyMiddleware
from app.models.order import Order


class _ExecResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class _FakeSession:
    def __init__(self, exec_values=None):
        self._exec_values = list(exec_values or [])
        self.added = []
        self.deleted = []
        self.commit_calls = 0
        self.rollback_calls = 0

    def exec(self, _statement):
        value = self._exec_values.pop(0) if self._exec_values else None
        return _ExecResult(value)

    def add(self, obj):
        self.added.append(obj)

    def delete(self, obj):
        self.deleted.append(obj)

    def flush(self):
        for obj in reversed(self.added):
            if isinstance(obj, Order) and obj.id is None:
                obj.id = 1
                return

    def commit(self):
        self.commit_calls += 1

    def refresh(self, _obj):
        return

    def rollback(self):
        self.rollback_calls += 1


def _build_app(session: _FakeSession, with_idempotency_middleware: bool = False) -> FastAPI:
    app = FastAPI()
    if with_idempotency_middleware:
        app.add_middleware(IdempotencyMiddleware)
    app.include_router(payments.router, prefix="/api/v1/payments")

    def _override_user():
        return SimpleNamespace(id=7, email="buyer@example.com")

    def _override_session():
        yield session

    app.dependency_overrides[payments.get_current_user] = _override_user
    app.dependency_overrides[payments.get_session] = _override_session
    return app


def test_create_order_returns_cached_response_for_same_idempotency_key(monkeypatch) -> None:
    session = _FakeSession()
    app = _build_app(session)

    class _CachedResponse:
        response_status_code = 200

        @staticmethod
        def get_response():
            return {"id": "cached_order", "amount": 999, "currency": "INR", "db_order_id": 77}

    async def _cached(*_args, **_kwargs):
        return _CachedResponse()

    def _should_not_call(*_args, **_kwargs):
        raise AssertionError("fresh checkout path should not run for cached idempotency key")

    monkeypatch.setattr(payments, "get_cached_response", _cached)
    monkeypatch.setattr(payments, "get_cart_with_items", _should_not_call)
    monkeypatch.setattr(payments, "create_razorpay_order", _should_not_call)

    client = TestClient(app)
    response = client.post(
        "/api/v1/payments/create-order",
        headers={"Idempotency-Key": "idem-key-123456"},
        json={"source": "test"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "cached_order",
        "amount": 999,
        "currency": "INR",
        "db_order_id": 77,
    }


def test_create_order_new_request_stores_idempotency_and_returns_order(monkeypatch) -> None:
    variant = SimpleNamespace(
        id=1,
        sku="sku-1",
        is_available=True,
        stock_quantity=10,
        price_adjustment=5.0,
        product=SimpleNamespace(id=50, price=100.0),
    )
    session = _FakeSession(exec_values=[variant])
    app = _build_app(session)

    stock_calls = []
    store_calls = []

    async def _not_cached(*_args, **_kwargs):
        return None

    async def _store_key(*args, **kwargs):
        store_calls.append({"args": args, "kwargs": kwargs})

    def _fake_cart(_session, _user_id):
        return SimpleNamespace(items=[SimpleNamespace(variant_id=1, quantity=2)])

    def _fake_razorpay_order(amount, notes):
        assert amount == 21000
        assert notes["user_id"] == "7"
        return {"id": "order_rzp_001", "amount": amount, "currency": "INR"}

    def _capture_deduct_stock(**kwargs):
        stock_calls.append(kwargs)

    monkeypatch.setattr(payments, "get_cached_response", _not_cached)
    monkeypatch.setattr(payments, "store_idempotency_key", _store_key)
    monkeypatch.setattr(payments, "get_cart_with_items", _fake_cart)
    monkeypatch.setattr(payments, "create_razorpay_order", _fake_razorpay_order)
    monkeypatch.setattr(payments, "deduct_stock_for_order", _capture_deduct_stock)

    client = TestClient(app)
    response = client.post(
        "/api/v1/payments/create-order",
        headers={"Idempotency-Key": "idem-key-123456"},
        json={"source": "test"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == "order_rzp_001"
    assert response.json()["db_order_id"] == 1

    assert len(stock_calls) == 1
    assert stock_calls[0]["quantity"] == 2
    assert stock_calls[0]["order_id"] == 1
    assert stock_calls[0]["user_id"] == 7

    assert len(store_calls) == 1
    store_args = store_calls[0]["args"]
    assert store_args[1] == "idem-key-123456"
    assert store_args[2] == 7
    assert store_args[3] == "/api/v1/payments/create-order"
    assert b'"source":"test"' in store_args[4]


def test_verify_endpoint_requires_idempotency_key_when_middleware_enabled() -> None:
    session = _FakeSession()
    app = _build_app(session, with_idempotency_middleware=True)

    client = TestClient(app)
    response = client.post(
        "/api/v1/payments/verify",
        json={
            "razorpay_order_id": "order_1",
            "razorpay_payment_id": "pay_1",
            "razorpay_signature": "sig_1",
        },
    )

    assert response.status_code == 400
    assert "Idempotency-Key header is required" in response.json()["detail"]


def test_verify_endpoint_succeeds_with_valid_idempotency_key(monkeypatch) -> None:
    order = Order(
        id=33,
        user_id=7,
        status="pending",
        total_amount=499.0,
        razorpay_order_id="order_1",
    )
    session = _FakeSession(exec_values=[order, None])
    app = _build_app(session, with_idempotency_middleware=True)

    monkeypatch.setattr(payments, "verify_payment_signature", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(payments, "send_order_confirmation", lambda *_args, **_kwargs: None)

    client = TestClient(app)
    response = client.post(
        "/api/v1/payments/verify",
        headers={"Idempotency-Key": "idem-key-123456"},
        json={
            "razorpay_order_id": "order_1",
            "razorpay_payment_id": "pay_1",
            "razorpay_signature": "sig_1",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "order_id": 33}
    assert order.status == "paid"
    assert order.razorpay_payment_id == "pay_1"
    assert session.commit_calls == 1