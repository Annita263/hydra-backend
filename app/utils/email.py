import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_order_confirmation(order) -> None:
    """Send a clean order confirmation email via Resend."""
    resend.Emails.send({
        "from": settings.FROM_EMAIL,
        "to": order.customer_email,
        "subject": f"Your HYDRA order is confirmed — {order.reference}",
        "html": f"""
        <div style="font-family:sans-serif;max-width:500px;margin:auto;padding:32px;">
          <h1 style="color:#1a1a1a;font-size:24px;">You're hydrated. ✓</h1>
          <p style="color:#444;font-size:16px;">
            Hi {order.customer_name}, your HYDRA order has been confirmed.
          </p>
          <div style="background:#f5f5f5;border-radius:8px;padding:20px;margin:24px 0;">
            <p style="margin:0 0 8px;color:#888;font-size:13px;">ORDER REFERENCE</p>
            <p style="margin:0;font-size:18px;font-weight:600;color:#1a1a1a;">{order.reference}</p>
          </div>
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="padding:8px 0;color:#888;font-size:14px;">Quantity</td>
              <td style="padding:8px 0;color:#1a1a1a;font-size:14px;text-align:right;">{order.quantity}</td>
            </tr>
            <tr style="border-top:1px solid #eee;">
              <td style="padding:12px 0;color:#1a1a1a;font-weight:600;font-size:15px;">Total paid</td>
              <td style="padding:12px 0;color:#1a1a1a;font-weight:600;font-size:15px;text-align:right;">₦{order.total_amount:,.0f}</td>
            </tr>
          </table>
          <p style="color:#888;font-size:13px;margin-top:32px;">
            We'll be in touch with delivery details shortly.<br/>
            — The HYDRA team
          </p>
        </div>
        """
    })
