import stripe
from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount: int, currency: str = "usd", metadata: dict = None):
    try:
        return stripe.PaymentIntent.create(
            amount=amount, 
            currency=currency,
            metadata=metadata or {}
        )
    except Exception as e:
        print(f"Stripe error: {e}")
        raise e

def construct_event(payload: bytes, sig_header: str):
    try:
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise e
