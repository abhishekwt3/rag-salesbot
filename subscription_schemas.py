# subscription_schemas.py - Pydantic schemas for subscription endpoints
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from models import SubscriptionPlan, SubscriptionStatus, PaymentStatus

# Plan Information
class PlanInfoResponse(BaseModel):
    plan: str
    name: str
    amount_usd: int
    amount_inr: int
    max_knowledge_bases: int
    max_total_chunks: int
    description: str
    features: List[str]

class PlansListResponse(BaseModel):
    plans: List[PlanInfoResponse]

# Subscription Creation
class SubscriptionCreateRequest(BaseModel):
    plan: SubscriptionPlan
    currency: Optional[str] = "INR"
    billing_cycle: Optional[str] = "monthly"

class SubscriptionCreateResponse(BaseModel):
    subscription_id: str
    razorpay_subscription_id: Optional[str]
    payment_link: Optional[str]
    trial_end: Optional[datetime]
    status: str
    message: str

# Current Subscription
class SubscriptionResponse(BaseModel):
    id: str
    plan: str
    status: str
    amount: int
    currency: str
    billing_cycle: str
    max_knowledge_bases: int
    max_total_chunks: int
    current_chunk_usage: int
    current_kb_count: int
    remaining_chunks: int
    trial_end: Optional[datetime]
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    is_trial_active: bool
    
    class Config:
        from_attributes = True

# Usage Information
class UsageResponse(BaseModel):
    current_chunk_usage: int
    max_total_chunks: int
    remaining_chunks: int
    current_kb_count: int
    max_knowledge_bases: int
    can_create_kb: bool
    plan: str
    status: str

# Payment Processing
class PaymentRequest(BaseModel):
    subscription_id: str
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

class PaymentResponse(BaseModel):
    status: str
    message: str
    payment_id: Optional[str]
    subscription_status: Optional[str]

# Payment History
class PaymentHistoryItem(BaseModel):
    id: str
    amount: int
    currency: str
    status: str
    payment_method: Optional[str]
    billing_period_start: Optional[datetime]
    billing_period_end: Optional[datetime]
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentHistoryResponse(BaseModel):
    payments: List[PaymentHistoryItem]
    total_payments: int

# Subscription Management
class SubscriptionUpdateRequest(BaseModel):
    plan: Optional[SubscriptionPlan] = None

class SubscriptionCancelRequest(BaseModel):
    cancel_at_cycle_end: Optional[bool] = True
    reason: Optional[str] = None

# Webhook Processing
class WebhookRequest(BaseModel):
    event: str
    payload: dict
    created_at: int

class WebhookResponse(BaseModel):
    status: str
    message: Optional[str] = None

# Usage Validation
class ChunkUsageValidation(BaseModel):
    can_add: bool
    current_usage: int
    max_allowed: int
    remaining: int
    message: str

class KnowledgeBaseValidation(BaseModel):
    can_create: bool
    current_count: int
    max_allowed: int
    message: str

# Billing Information
class BillingInfoResponse(BaseModel):
    next_billing_date: Optional[datetime]
    amount_due: int
    currency: str
    billing_cycle: str
    payment_method: Optional[str]
    auto_renewal: bool

# Subscription Upgrade/Downgrade
class PlanChangeRequest(BaseModel):
    new_plan: SubscriptionPlan
    immediate: Optional[bool] = False  # Apply immediately or at next billing cycle

class PlanChangeResponse(BaseModel):
    success: bool
    message: str
    effective_date: Optional[datetime]
    prorated_amount: Optional[int]
    new_subscription_id: Optional[str]

# Trial Extension
class TrialExtensionRequest(BaseModel):
    days: int
    reason: Optional[str] = None

class TrialExtensionResponse(BaseModel):
    success: bool
    new_trial_end: Optional[datetime]
    message: str