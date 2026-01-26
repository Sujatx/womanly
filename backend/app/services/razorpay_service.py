import razorpay
from app.config import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount: int, currency: str = "INR", notes: dict = None):
    """
    Amount should be in the smallest currency unit (e.g., paise for INR).
    """
    data = {
        "amount": amount,
        "currency": currency,
        "notes": notes or {},
        "payment_capture": 1 # Auto-capture
    }
    try:
        order = client.order.create(data=data)
        return order
    except Exception as e:
        print(f"Razorpay error: {e}")
        raise e

def verify_payment_signature(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        return client.utility.verify_payment_signature(params_dict)
    except Exception:
        return False
