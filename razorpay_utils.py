# razorpay_utils.py - Razorpay integration utilities
import os
import razorpay
import hmac
import hashlib
import logging
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from models import SubscriptionPlan, SubscriptionStatus, PaymentStatus

logger = logging.getLogger(__name__)

class RazorpayManager:
    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        
        if not self.key_id or not self.key_secret:
            logger.warning("Razorpay credentials not found. Payment features disabled.")
            self.client = None
        else:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            logger.info("✅ Razorpay client initialized")
    
    def is_available(self) -> bool:
        """Check if Razorpay is properly configured"""
        return self.client is not None
    
    def create_plan(self, plan_type: SubscriptionPlan, currency: str = "INR") -> Optional[Dict]:
        """Create a Razorpay plan"""
        if not self.is_available():
            return None
        
        plan_details = {
            SubscriptionPlan.BASIC: {
                "id": "basic_monthly",
                "name": "Basic Plan",
                "amount": 42000 if currency == "INR" else 500,  # ₹420 or $5
                "description": "5 knowledge bases, 200 data chunks"
            },
            SubscriptionPlan.PRO: {
                "id": "pro_monthly", 
                "name": "Pro Plan",
                "amount": 210000 if currency == "INR" else 2500,  # ₹2100 or $25
                "description": "30 knowledge bases, 1500 data chunks"
            },
            SubscriptionPlan.ENTERPRISE: {
                "id": "enterprise_monthly",
                "name": "Enterprise Plan", 
                "amount": 1680000 if currency == "INR" else 20000,  # ₹16800 or $200
                "description": "Unlimited knowledge bases and chunks"
            }
        }
        
        plan_info = plan_details[plan_type]
        
        try:
            # Check if plan already exists
            try:
                existing_plan = self.client.plan.fetch(plan_info["id"])
                logger.info(f"Using existing Razorpay plan: {plan_info['id']}")
                return existing_plan
            except razorpay.errors.BadRequestError:
                # Plan doesn't exist, create new one
                pass
            
            plan_data = {
                "id": plan_info["id"],
                "item": {
                    "name": plan_info["name"],
                    "amount": plan_info["amount"],
                    "currency": currency,
                    "description": plan_info["description"]
                },
                "period": "monthly",
                "interval": 1,
                "notes": {
                    "plan_type": plan_type.value,
                    "max_kb": str(plan_details[plan_type].get("max_knowledge_bases", -1)),
                    "max_chunks": str(plan_details[plan_type].get("max_total_chunks", -1))
                }
            }
            
            plan = self.client.plan.create(plan_data)
            logger.info(f"✅ Created Razorpay plan: {plan_info['id']}")
            return plan
            
        except Exception as e:
            logger.error(f"❌ Error creating Razorpay plan: {e}")
            return None
    
    def create_customer(self, email: str, name: str, phone: str = None) -> Optional[Dict]:
        """Create a Razorpay customer"""
        if not self.is_available():
            return None
        
        try:
            customer_data = {
                "name": name,
                "email": email,
                "contact": phone or "",
                "fail_existing": "0"  # Don't fail if customer already exists
            }
            
            customer = self.client.customer.create(customer_data)
            logger.info(f"✅ Created Razorpay customer: {customer['id']}")
            return customer
            
        except Exception as e:
            logger.error(f"❌ Error creating Razorpay customer: {e}")
            return None
    
    def create_subscription(self, customer_id: str, plan_id: str, total_count: int = 12) -> Optional[Dict]:
        """Create a Razorpay subscription"""
        if not self.is_available():
            return None
        
        try:
            subscription_data = {
                "plan_id": plan_id,
                "customer_id": customer_id,
                "total_count": total_count,  # 12 months
                "quantity": 1,
                "start_at": int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp()),  # 7-day trial
                "expire_by": int((datetime.now(timezone.utc) + timedelta(days=365)).timestamp()),  # 1 year expiry
                "notes": {
                    "created_via": "saas_api",
                    "trial_period": "7_days"
                }
            }
            
            subscription = self.client.subscription.create(subscription_data)
            logger.info(f"✅ Created Razorpay subscription: {subscription['id']}")
            return subscription
            
        except Exception as e:
            logger.error(f"❌ Error creating Razorpay subscription: {e}")
            return None
    
    def create_payment_link(self, amount: int, currency: str, customer_email: str, 
                          description: str, subscription_id: str = None) -> Optional[Dict]:
        """Create a payment link for one-time payments"""
        if not self.is_available():
            return None
        
        try:
            payment_link_data = {
                "amount": amount,
                "currency": currency,
                "accept_partial": False,
                "description": description,
                "customer": {
                    "email": customer_email
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "notes": {
                    "subscription_id": subscription_id or "",
                    "created_via": "saas_api"
                },
                "callback_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/callback",
                "callback_method": "get"
            }
            
            payment_link = self.client.payment_link.create(payment_link_data)
            logger.info(f"✅ Created payment link: {payment_link['id']}")
            return payment_link
            
        except Exception as e:
            logger.error(f"❌ Error creating payment link: {e}")
            return None
    
    def verify_payment_signature(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Verify Razorpay payment signature"""
        if not self.is_available():
            return False
        
        try:
            # Create the message to verify
            message = f"{order_id}|{payment_id}"
            
            # Generate signature
            generated_signature = hmac.new(
                self.key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(generated_signature, signature)
            
        except Exception as e:
            logger.error(f"❌ Error verifying payment signature: {e}")
            return False
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """Get payment details from Razorpay"""
        if not self.is_available():
            return None
        
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"❌ Error fetching payment details: {e}")
            return None
    
    def get_subscription_details(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details from Razorpay"""
        if not self.is_available():
            return None
        
        try:
            subscription = self.client.subscription.fetch(subscription_id)
            return subscription
        except Exception as e:
            logger.error(f"❌ Error fetching subscription details: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str, cancel_at_cycle_end: bool = True) -> Optional[Dict]:
        """Cancel a Razorpay subscription"""
        if not self.is_available():
            return None
        
        try:
            cancel_data = {
                "cancel_at_cycle_end": cancel_at_cycle_end
            }
            
            result = self.client.subscription.cancel(subscription_id, cancel_data)
            logger.info(f"✅ Canceled Razorpay subscription: {subscription_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error canceling subscription: {e}")
            return None
    
    def handle_webhook(self, event_data: Dict) -> Dict:
        """Handle Razorpay webhook events"""
        event_type = event_data.get("event")
        payload = event_data.get("payload", {})
        
        logger.info(f"📡 Received Razorpay webhook: {event_type}")
        
        result = {"status": "processed", "event": event_type}
        
        try:
            if event_type == "payment.captured":
                # Payment successful
                payment = payload.get("payment", {}).get("entity", {})
                result["payment_id"] = payment.get("id")
                result["status"] = "payment_success"
                
            elif event_type == "payment.failed":
                # Payment failed
                payment = payload.get("payment", {}).get("entity", {})
                result["payment_id"] = payment.get("id")
                result["status"] = "payment_failed"
                result["error"] = payment.get("error_description")
                
            elif event_type == "subscription.activated":
                # Subscription activated
                subscription = payload.get("subscription", {}).get("entity", {})
                result["subscription_id"] = subscription.get("id")
                result["status"] = "subscription_activated"
                
            elif event_type == "subscription.cancelled":
                # Subscription cancelled
                subscription = payload.get("subscription", {}).get("entity", {})
                result["subscription_id"] = subscription.get("id")
                result["status"] = "subscription_cancelled"
                
            elif event_type == "subscription.charged":
                # Subscription payment charged
                subscription = payload.get("subscription", {}).get("entity", {})
                result["subscription_id"] = subscription.get("id")
                result["status"] = "subscription_charged"
                
            else:
                logger.info(f"Unhandled webhook event: {event_type}")
                result["status"] = "unhandled"
                
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result

# Global instance
razorpay_manager = RazorpayManager()