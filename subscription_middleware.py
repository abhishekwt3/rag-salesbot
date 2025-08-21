# subscription_middleware.py - Fixed with correct imports
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, KnowledgeBase, get_db, Subscription, SubscriptionPlan, SubscriptionStatus
from auth import get_current_user  # ADDED MISSING IMPORT
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class SubscriptionManager:
    def __init__(self):
        pass
    
    def get_or_create_subscription(self, user: User, db: Session) -> Subscription:
        """Get user's subscription or create a trial subscription"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()
        
        if not subscription:
            # Create a 7-day trial subscription with Basic plan
            trial_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
            trial_end = trial_end.replace(day=trial_end.day + 7)  # 7-day trial
            
            plan_details = Subscription.get_plan_details(SubscriptionPlan.BASIC)
            
            subscription = Subscription(
                user_id=user.id,
                plan=SubscriptionPlan.BASIC,
                status=SubscriptionStatus.TRIALING,
                amount=plan_details["amount_inr"],
                currency="INR",
                max_knowledge_bases=plan_details["max_knowledge_bases"],
                max_total_chunks=plan_details["max_total_chunks"],
                trial_start=datetime.now(timezone.utc),
                trial_end=trial_end,
                current_chunk_usage=0,
                current_kb_count=0
            )
            
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            logger.info(f"✅ Created trial subscription for user {user.email}")
        
        return subscription
    
    def update_chunk_usage(self, user_id: str, delta_chunks: int, db: Session):
        """Update chunk usage for a user's subscription"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if subscription:
            subscription.current_chunk_usage = max(0, subscription.current_chunk_usage + delta_chunks)
            db.commit()
            logger.info(f"📊 Updated chunk usage for user {user_id}: delta={delta_chunks}, total={subscription.current_chunk_usage}")
    
    def update_kb_count(self, user_id: str, delta_kb: int, db: Session):
        """Update knowledge base count for a user's subscription"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if subscription:
            subscription.current_kb_count = max(0, subscription.current_kb_count + delta_kb)
            db.commit()
            logger.info(f"📚 Updated KB count for user {user_id}: delta={delta_kb}, total={subscription.current_kb_count}")
    
    def recalculate_usage(self, user_id: str, db: Session):
        """Recalculate actual usage from database"""
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if not subscription:
            return
        
        # Count actual knowledge bases
        kb_count = db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == user_id
        ).count()
        
        # Sum total chunks across all knowledge bases
        total_chunks = db.query(KnowledgeBase).filter(
            KnowledgeBase.user_id == user_id
        ).with_entities(db.func.sum(KnowledgeBase.total_chunks)).scalar() or 0
        
        # Update subscription
        subscription.current_kb_count = kb_count
        subscription.current_chunk_usage = total_chunks
        db.commit()
        
        logger.info(f"🔄 Recalculated usage for user {user_id}: KBs={kb_count}, chunks={total_chunks}")

# Global instance
subscription_manager = SubscriptionManager()

# Dependency functions for FastAPI
def get_user_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Subscription:
    """FastAPI dependency to get user's subscription"""
    return subscription_manager.get_or_create_subscription(current_user, db)

def check_subscription_active(subscription: Subscription = Depends(get_user_subscription)) -> Subscription:
    """Check if subscription is active (including trial)"""
    if not subscription.is_subscription_active():
        if subscription.status == SubscriptionStatus.EXPIRED:
            raise HTTPException(
                status_code=402, 
                detail="Your subscription has expired. Please renew to continue using the service."
            )
        elif subscription.status == SubscriptionStatus.CANCELED:
            raise HTTPException(
                status_code=402,
                detail="Your subscription has been canceled. Please reactivate to continue."
            )
        else:
            raise HTTPException(
                status_code=402,
                detail="Your subscription is not active. Please check your payment status."
            )
    
    return subscription

def check_can_create_kb(subscription: Subscription = Depends(check_subscription_active)) -> Subscription:
    """Check if user can create a new knowledge base"""
    if not subscription.can_create_knowledge_base():
        remaining = subscription.max_knowledge_bases - subscription.current_kb_count
        raise HTTPException(
            status_code=403,
            detail=f"Knowledge base limit reached. You have {subscription.current_kb_count}/{subscription.max_knowledge_bases} knowledge bases. Upgrade your plan to create more."
        )
    
    return subscription

def check_can_add_chunks(chunk_count: int):
    """Create a dependency to check if user can add specified chunks"""
    def _check_chunks(subscription: Subscription = Depends(check_subscription_active)) -> Subscription:
        if not subscription.can_add_chunks(chunk_count):
            remaining = subscription.get_remaining_chunks()
            raise HTTPException(
                status_code=403,
                detail=f"Data chunk limit reached. You need {chunk_count} chunks but only have {remaining} remaining. Current usage: {subscription.current_chunk_usage}/{subscription.max_total_chunks}. Upgrade your plan to add more data."
            )
        
        return subscription
    
    return _check_chunks

# Usage validation functions
def validate_chunk_addition(user_id: str, chunk_count: int, db: Session) -> dict:
    """Validate if chunks can be added and return detailed info"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()
    
    if not subscription:
        subscription = subscription_manager.get_or_create_subscription(
            db.query(User).filter(User.id == user_id).first(), db
        )
    
    can_add = subscription.can_add_chunks(chunk_count)
    remaining = subscription.get_remaining_chunks()
    
    return {
        "can_add": can_add,
        "current_usage": subscription.current_chunk_usage,
        "max_allowed": subscription.max_total_chunks,
        "remaining": remaining,
        "chunks_requested": chunk_count,
        "plan": subscription.plan.value,
        "message": f"You can add {chunk_count} chunks" if can_add else f"Cannot add {chunk_count} chunks. Only {remaining} chunks remaining."
    }

def validate_kb_creation(user_id: str, db: Session) -> dict:
    """Validate if knowledge base can be created"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()
    
    if not subscription:
        subscription = subscription_manager.get_or_create_subscription(
            db.query(User).filter(User.id == user_id).first(), db
        )
    
    can_create = subscription.can_create_knowledge_base()
    
    return {
        "can_create": can_create,
        "current_count": subscription.current_kb_count,
        "max_allowed": subscription.max_knowledge_bases,
        "plan": subscription.plan.value,
        "message": "You can create a new knowledge base" if can_create else f"Cannot create KB. Limit reached: {subscription.current_kb_count}/{subscription.max_knowledge_bases}"
    }

# Context managers for usage tracking
class ChunkUsageTracker:
    """Context manager to track chunk usage"""
    def __init__(self, user_id: str, chunk_count: int, db: Session):
        self.user_id = user_id
        self.chunk_count = chunk_count
        self.db = db
        self.added = False
    
    def __enter__(self):
        # Validate before adding
        validation = validate_chunk_addition(self.user_id, self.chunk_count, self.db)
        if not validation["can_add"]:
            raise HTTPException(status_code=403, detail=validation["message"])
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Only update usage if no exception occurred
        if exc_type is None and self.added:
            subscription_manager.update_chunk_usage(self.user_id, self.chunk_count, self.db)
    
    def mark_added(self):
        """Mark chunks as successfully added"""
        self.added = True

class KBUsageTracker:
    """Context manager to track knowledge base usage"""
    def __init__(self, user_id: str, db: Session):
        self.user_id = user_id
        self.db = db
        self.created = False
    
    def __enter__(self):
        # Validate before creating
        validation = validate_kb_creation(self.user_id, self.db)
        if not validation["can_create"]:
            raise HTTPException(status_code=403, detail=validation["message"])
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Only update usage if no exception occurred
        if exc_type is None and self.created:
            subscription_manager.update_kb_count(self.user_id, 1, self.db)
    
    def mark_created(self):
        """Mark KB as successfully created"""
        self.created = True