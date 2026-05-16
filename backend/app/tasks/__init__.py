"""Task package for Celery background jobs."""
# Import to ensure tasks are registered when Celery autodiscovers
from . import email

__all__ = ["email"]
