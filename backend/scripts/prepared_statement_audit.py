"""Simple prepared-statement safety check for product search queries.

Usage:
    python scripts/prepared_statement_audit.py
"""

from sqlmodel import Session, select, col
from app.db import get_read_session
from app.models.product import Product


def run_audit() -> None:
    injection_like_input = "ABC'; DROP TABLE products; --"

    session: Session = next(get_read_session())
    try:
        query = select(Product).where(col(Product.title).ilike(f"%{injection_like_input}%"))
        _ = session.exec(query).all()
        print("OK: Parameterized query executed safely with injection-like input.")
    finally:
        session.close()


if __name__ == "__main__":
    run_audit()
