import ssl
from email.message import EmailMessage
from aiosmtplib import send
from app.config import settings

async def send_email(subject: str, to: str, html_content: str):
    """Core async email sender."""
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.add_alternative(html_content, subtype="html")

    # Connect and send
    await send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_PORT == 587,
    )

async def send_verification_email(email: str, token: str):
    """Sends the VEXO-styled verification email."""
    # Note: In production, this would be a real URL. 
    # For now, it's the frontend verification link.
    verify_url = f"http://localhost:3000/auth/verify?token={token}"
    
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 24px;">
        <h1 style="font-size: 24px; font-weight: 900; letter-spacing: 0.05em; text-transform: uppercase;">Womanly</h1>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 16px; font-weight: 600; color: #64748b;">PLEASE VERIFY YOUR ACCOUNT</p>
        <p style="font-size: 14px; line-height: 1.6; color: #1e293b;">
            Welcome to Womanly. Click the button below to verify your email address and activate your account.
        </p>
        <a href="{verify_url}" style="display: inline-block; padding: 14px 28px; background: #0f172a; color: white; text-decoration: none; border-radius: 32px; font-weight: 900; font-size: 12px; margin-top: 20px; text-transform: uppercase;">
            VERIFY ACCOUNT
        </a>
        <p style="font-size: 12px; color: #94a3b8; margin-top: 40px;">
            If you didn't create an account, you can safely ignore this email.
        </p>
    </div>
    """
    await send_email("Verify your Womanly account", email, html)

async def send_order_confirmation(email: str, order_id: int, amount: float):
    """Sends order confirmation details."""
    html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 24px;">
        <h1 style="font-size: 24px; font-weight: 900; letter-spacing: 0.05em; text-transform: uppercase;">Womanly</h1>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 16px; font-weight: 600; color: #64748b;">ORDER CONFIRMED</p>
        <p style="font-size: 14px; line-height: 1.6; color: #1e293b;">
            Thank you for your purchase. Your order <strong>#{order_id}</strong> has been received and is being processed.
        </p>
        <div style="background: #f8fafc; padding: 20px; border-radius: 16px; margin: 20px 0;">
            <p style="margin: 0; font-size: 12px; font-weight: 800; color: #64748b;">TOTAL AMOUNT</p>
            <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 900;">${amount}</p>
        </div>
        <a href="http://localhost:3000/account/orders" style="display: inline-block; padding: 14px 28px; background: #0f172a; color: white; text-decoration: none; border-radius: 32px; font-weight: 900; font-size: 12px; text-transform: uppercase;">
            VIEW ORDER STATUS
        </a>
    </div>
    """
    await send_email(f"Order Confirmation #{order_id}", email, html)
