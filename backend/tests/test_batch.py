import types
from app.api.batch import batch_get_products, ProductBatchRequest


class FakeResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class FakeSession:
    def __init__(self, result_items=None):
        self._result_items = result_items or []

    def exec(self, *args, **kwargs):
        return FakeResult(self._result_items)


def test_batch_get_products_empty(monkeypatch):
    class FakeProductRepo:
        def get_many_by_ids(self, session, ids, include_variants=True, include_images=True):
            return []

    monkeypatch.setattr("app.di_container.get", lambda name: FakeProductRepo())

    session = FakeSession(result_items=[])
    req = ProductBatchRequest(product_ids=[1, 2])

    import asyncio
    res = asyncio.run(batch_get_products(req, session=session))

    assert res.products == []
    assert res.not_found == [1, 2]
