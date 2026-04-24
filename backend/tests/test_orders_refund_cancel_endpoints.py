from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api import orders as orders_api
from app.models.order import Order


class _ExecResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class _FakeSession:
    def __init__(self, existing_refund=None):
        self._existing_refund = existing_refund
        self.added = []
        self.commit_calls = 0

    def exec(self, _statement):
        return _ExecResult(self._existing_refund)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.commit_calls += 1

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = 1001


def test_cancel_order_pending_transitions_and_restores_inventory(monkeypatch) -> None:
    order = Order(id=10, user_id=7, status="pending", total_amount=499.0)
    session = _FakeSession()
    current_user = SimpleNamespace(id=7)

    restore_calls = []

    def _fake_get_order(_session, _order_id, _user_id):
        return order

    def _capture_restore_inventory(_session, _order, _user_id):
        restore_calls.append((_order.id, _user_id))

    monkeypatch.setattr(orders_api, "_get_order_or_404", _fake_get_order)
    monkeypatch.setattr(orders_api, "_restore_inventory", _capture_restore_inventory)

    response = orders_api.cancel_order(order_id=10, current_user=current_user, session=session)

    assert response["status"] == "cancelled"
    assert response["order_id"] == 10
    assert response["refund_id"] is None
    assert order.status == "cancelled"
    assert restore_calls == [(10, 7)]
    assert session.commit_calls == 1


def test_request_refund_paid_order_processes_and_cancels(monkeypatch) -> None:
    order = Order(
        id=11,
        user_id=7,
        status="paid",
        total_amount=799.0,
        razorpay_payment_id="pay_123",
    )
    session = _FakeSession(existing_refund=None)
    current_user = SimpleNamespace(id=7)

    restore_calls = []

    def _fake_get_order(_session, _order_id, _user_id):
        return order

    def _fake_refund(payment_id, amount, notes):
        assert payment_id == "pay_123"
        assert amount == 79900
        assert notes["order_id"] == "11"
        return {"id": "rf_abc"}

    def _capture_restore_inventory(_session, _order, _user_id):
        restore_calls.append((_order.id, _user_id))

    monkeypatch.setattr(orders_api, "_get_order_or_404", _fake_get_order)
    monkeypatch.setattr(orders_api, "create_razorpay_refund", _fake_refund)
    monkeypatch.setattr(orders_api, "_restore_inventory", _capture_restore_inventory)

    response = orders_api.request_refund(
        body=orders_api.RefundRequest(reason="Item damaged"),
        order_id=11,
        current_user=current_user,
        session=session,
    )

    assert response["status"] == "processed"
    assert response["razorpay_refund_id"] == "rf_abc"
    assert order.status == "cancelled"
    assert restore_calls == [(11, 7)]
    assert session.commit_calls == 1


def test_request_refund_gateway_failure_records_and_raises(monkeypatch) -> None:
    order = Order(
        id=12,
        user_id=9,
        status="paid",
        total_amount=159.0,
        razorpay_payment_id="pay_999",
    )
    session = _FakeSession(existing_refund=None)
    current_user = SimpleNamespace(id=9)

    restore_calls = []

    def _fake_get_order(_session, _order_id, _user_id):
        return order

    def _fake_refund_failure(**_kwargs):
        raise RuntimeError("gateway unavailable")

    def _capture_restore_inventory(_session, _order, _user_id):
        restore_calls.append((_order.id, _user_id))

    monkeypatch.setattr(orders_api, "_get_order_or_404", _fake_get_order)
    monkeypatch.setattr(orders_api, "create_razorpay_refund", _fake_refund_failure)
    monkeypatch.setattr(orders_api, "_restore_inventory", _capture_restore_inventory)

    with pytest.raises(HTTPException) as exc_info:
        orders_api.request_refund(
            body=orders_api.RefundRequest(reason="Late delivery"),
            order_id=12,
            current_user=current_user,
            session=session,
        )

    assert exc_info.value.status_code == 502
    assert "Refund request recorded" in exc_info.value.detail
    assert order.status == "paid"
    assert restore_calls == []
    assert session.commit_calls == 1