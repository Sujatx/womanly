import asyncio
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from sqlmodel import Session, SQLModel, create_engine, select

from app.middleware.idempotency import get_cached_response, store_idempotency_key
from app.models.idempotency import IdempotencyKey
from app.models.user import User


def _create_session_with_user() -> tuple[Session, User]:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine, tables=[User.__table__, IdempotencyKey.__table__])

    session = Session(engine)
    user = User(email="idempotency-test@example.com", hashed_password="hashed")
    session.add(user)
    session.commit()
    session.refresh(user)
    return session, user


def test_store_and_retrieve_cached_response() -> None:
    session, user = _create_session_with_user()
    try:
        endpoint = "/api/v1/payments/create-order"
        key = "idem-key-12345678"
        request_body = b'{"cart_id":1,"amount":1000}'
        response_json = '{"id":"order_123","amount":1000}'

        asyncio.run(
            store_idempotency_key(
                session=session,
                idempotency_key=key,
                user_id=user.id,
                endpoint=endpoint,
                request_body=request_body,
                response_json=response_json,
                response_status=200,
            )
        )

        cached = asyncio.run(
            get_cached_response(
                session=session,
                idempotency_key=key,
                endpoint=endpoint,
                user_id=user.id,
            )
        )

        assert cached is not None
        assert cached.request_hash == sha256(request_body).hexdigest()
        assert cached.response_status_code == 200
        assert cached.get_response() == {"id": "order_123", "amount": 1000}
    finally:
        session.close()


def test_expired_idempotency_key_is_deleted_and_not_returned() -> None:
    session, user = _create_session_with_user()
    try:
        endpoint = "/api/v1/payments/create-order"
        key = "idem-key-expired-123456"

        expired = IdempotencyKey(
            idempotency_key=key,
            user_id=user.id,
            endpoint=endpoint,
            request_hash=sha256(b"{}").hexdigest(),
            response_json='{"status":"stale"}',
            response_status_code=200,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        session.add(expired)
        session.commit()

        cached = asyncio.run(
            get_cached_response(
                session=session,
                idempotency_key=key,
                endpoint=endpoint,
                user_id=user.id,
            )
        )

        assert cached is None

        remaining = session.exec(
            select(IdempotencyKey).where(IdempotencyKey.idempotency_key == key)
        ).first()
        assert remaining is None
    finally:
        session.close()