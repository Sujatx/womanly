from types import SimpleNamespace

from app.api import orders as orders_api


class _ExecResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value


class _FakeSession:
    def __init__(self, direct_variant=None, fallback_variant=None):
        self._direct_variant = direct_variant
        self._fallback_variant = fallback_variant

    def get(self, _model, _identifier):
        return self._direct_variant

    def exec(self, _statement):
        return _ExecResult(self._fallback_variant)


def test_restore_inventory_uses_direct_variant_lookup(monkeypatch) -> None:
    variant = SimpleNamespace(id=11)
    order = SimpleNamespace(id=42, items=[SimpleNamespace(product_id=11, quantity=2)])
    session = _FakeSession(direct_variant=variant, fallback_variant=None)

    calls = []

    def _capture_refund_stock_for_order(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(orders_api, "refund_stock_for_order", _capture_refund_stock_for_order)

    orders_api._restore_inventory(session=session, order=order, user_id=7)

    assert len(calls) == 1
    assert calls[0]["variant"] is variant
    assert calls[0]["quantity"] == 2
    assert calls[0]["order_id"] == 42
    assert calls[0]["user_id"] == 7


def test_restore_inventory_falls_back_to_product_variant_query(monkeypatch) -> None:
    fallback_variant = SimpleNamespace(id=99)
    order = SimpleNamespace(id=43, items=[SimpleNamespace(product_id=501, quantity=1)])
    session = _FakeSession(direct_variant=None, fallback_variant=fallback_variant)

    calls = []

    def _capture_refund_stock_for_order(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(orders_api, "refund_stock_for_order", _capture_refund_stock_for_order)

    orders_api._restore_inventory(session=session, order=order, user_id=9)

    assert len(calls) == 1
    assert calls[0]["variant"] is fallback_variant
    assert calls[0]["quantity"] == 1
    assert calls[0]["order_id"] == 43
    assert calls[0]["user_id"] == 9