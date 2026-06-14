import stripe
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger("stripe_service")

class StripeService:
    def __init__(self):
        self.active = bool(settings.STRIPE_API_KEY)
        if self.active:
            stripe.api_key = settings.STRIPE_API_KEY
        else:
            logger.warning("STRIPE_API_KEY is not configured. Payments will run in MOCK mode.")

    async def create_checkout_session(self, user_id: str, email: str, plan_type: str, success_url: str, cancel_url: str) -> str:
        """
        Creates a Stripe checkout session, or returns a mock callback URL if Stripe is inactive.
        """
        if not self.active:
            # Generate mock redirect URL
            mock_session_id = f"cs_test_mock_{user_id}_{plan_type}"
            logger.info(f"Stripe is mock: Redirecting user to success page with session {mock_session_id}")
            # Append session id and plan type to success url
            return f"{success_url}?session_id={mock_session_id}&plan={plan_type}"

        try:
            # Price configuration. In production, define prices in Stripe Dashboard.
            price_id = "price_pro_monthly"  # placeholder or load from settings
            
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=email,
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"Resume Intelligence Platform - {plan_type.upper()} Plan",
                                "description": "Unlimited resume optimizations, ATS reports, and cover letters.",
                            },
                            "unit_amount": 2900 if plan_type == "pro" else 0, # $29/month
                            "recurring": {"interval": "month"},
                        },
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                metadata={"user_id": user_id, "plan": plan_type},
                success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&plan={plan_type}",
                cancel_url=cancel_url,
            )
            return session.url
        except Exception as e:
            logger.error(f"Failed to create Stripe Checkout session: {e}")
            raise RuntimeError(f"Payment gateway error: {str(e)}")

    def construct_event(self, payload: bytes, sig_header: str) -> Optional[stripe.Event]:
        """
        Validates the Stripe webhook signature and returns the event object.
        """
        if not self.active:
            # Return a mock event if payload contains mocked signature or local testing
            try:
                data = json.loads(payload.decode())
                return stripe.Event.construct_from(data, None)
            except Exception:
                return None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe signature: {e}")
            raise ValueError("Invalid signature")

stripe_service = StripeService()
