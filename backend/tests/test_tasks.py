import sys
import types
import json

import pytest


def _insert_fake_celery_module():
    """Insert a minimal fake `celery` module into sys.modules for tests.

    This avoids requiring Celery to be installed to import task modules.
    """
    fake_celery = types.SimpleNamespace()

    class DummyCelery:
        def __init__(self, app_name, broker=None, backend=None):
            self.conf = {}

        def task(self, bind=False, name=None, max_retries=None):
            def decorator(func):
                # Return a simple object with `run` that calls the function
                class TaskWrapper:
                    def __init__(self, func):
                        self._func = func

                    def run(self, *args, **kwargs):
                        # If caller already passed a bound `self` (None), call directly
                        if len(args) > 0 and args[0] is None:
                            return self._func(*args, **kwargs)
                        # Otherwise, supply a dummy `self` as the first arg
                        return self._func(None, *args, **kwargs)

                    def __call__(self, *args, **kwargs):
                        return self.run(*args, **kwargs)

                return TaskWrapper(func)

            return decorator

        def autodiscover_tasks(self, *args, **kwargs):
            return None

    fake_celery.Celery = DummyCelery

    # signals.task_failure with connect method
    signals_mod = types.SimpleNamespace()

    class DummySignal:
        def connect(self, fn):
            return None

    signals_mod.task_failure = DummySignal()
    fake_celery.signals = signals_mod

    sys.modules["celery"] = fake_celery
    sys.modules["celery.signals"] = signals_mod


def test_send_order_confirmation_success(monkeypatch):
    _insert_fake_celery_module()

    # Import tasks after inserting fake celery
    from app.tasks.email import send_order_confirmation

    res = send_order_confirmation.run(None, "test@example.com", "Hi", "Body")
    assert isinstance(res, dict)
    assert res.get("status") == "sent"


def test_sync_inventory_success(monkeypatch):
    _insert_fake_celery_module()

    from app.tasks.inventory import sync_inventory

    res = sync_inventory.run(None, "warehouse_api")
    assert isinstance(res, dict)
    assert res.get("status") == "ok"


def test_push_to_dlq(monkeypatch):
    # Fake redis client capturing lpush
    calls = {}

    class FakeRedis:
        def __init__(self, *args, **kwargs):
            pass

        def lpush(self, key, value):
            calls.setdefault("lpush", []).append((key, value))

    monkeypatch.setattr("redis.from_url", lambda *a, **k: FakeRedis())

    from app.tasks.utils import push_to_dlq

    push_to_dlq("task.name", "tid-1", [1, 2], {"a": 1}, Exception("boom"))
    assert "lpush" in calls
    key, val = calls["lpush"][0]
    assert key == "womanly:dlq"
    data = json.loads(val)
    assert data["task_name"] == "task.name"
