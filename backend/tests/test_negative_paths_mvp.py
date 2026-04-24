import asyncio
from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks, HTTPException

from app.api import auth, discounts, payments
from app.core.exceptions import InsufficientStockException, InvalidSignatureException


class _ExecResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class _FakeSession:
    def __init__(self, exec_values=None):
        self._exec_values = list(exec_values or [])
        self.rollback_calls = 0

    def exec(self, _statement):
        value = self._exec_values.pop(0) if self._exec_values else None
        return _ExecResult(value)

    def rollback(self):
        self.rollback_calls += 1


def test_create_order_raises_insufficient_stock_and_rolls_back(monkeypatch) -> None:
    variant = SimpleNamespace(
        id=1,
        sku="sku-low-stock",
        stock_quantity=1,
        is_available=True,
        product=SimpleNamespace(id=99, price=100.0),
        price_adjustment=0.0,
    )
    session = _FakeSession(exec_values=[variant])

    async def _not_cached(*_args, **_kwargs):
        return None

    def _fake_cart(_session, _user_id):
        return SimpleNamespace(items=[SimpleNamespace(variant_id=1, quantity=2)])

    monkeypatch.setattr(payments, "get_cached_response", _not_cached)
    monkeypatch.setattr(payments, "get_cart_with_items", _fake_cart)

    with pytest.raises(InsufficientStockException):
        asyncio.run(
            payments.create_order(
                current_user=SimpleNamespace(id=7),
                session=session,
                request=None,
                idempotency_key="idem-key-123456",
            )
        )

    assert session.rollback_calls == 1


def test_verify_payment_raises_invalid_signature_exception(monkeypatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr(payments, "verify_payment_signature", lambda *_args, **_kwargs: False)

    with pytest.raises(InvalidSignatureException):
        asyncio.run(
            payments.verify_payment(
                data=payments.PaymentVerify(
                    razorpay_order_id="order_1",
                    razorpay_payment_id="pay_1",
                    razorpay_signature="sig_bad",
                ),
                background_tasks=BackgroundTasks(),
                current_user=SimpleNamespace(id=7),
                session=session,
            )
        )


def test_validate_coupon_returns_not_found_for_unknown_code() -> None:
    session = _FakeSession(exec_values=[None])

    response = discounts.validate_coupon(
        code="DOESNOTEXIST",
        order_total=500.0,
        current_user=SimpleNamespace(id=7),
        session=session,
    )

    assert response.valid is False
    assert response.message == "Coupon code not found."


def test_login_email_returns_401_for_invalid_credentials(monkeypatch) -> None:
    user = SimpleNamespace(id=1, email="user@example.com", hashed_password="hash", is_active=True)
    session = _FakeSession(exec_values=[user])

    monkeypatch.setattr(auth, "verify_password", lambda *_args, **_kwargs: False)

    with pytest.raises(HTTPException) as exc_info:
        auth.login_email(auth.LoginRequest(email="user@example.com", password="wrong"), session=session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"