# oauth.py - OAuth Authentication for Google and Apple Sign-In
import os
import httpx
import jwt
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

# Import your existing auth and models
from auth import create_access_token
from models import User, get_db

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Create OAuth router
oauth_router = APIRouter(prefix="/auth", tags=["OAuth"])

# In-memory state storage (use Redis in production)
oauth_states = {}

@oauth_router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "google", "timestamp": datetime.utcnow()}
    
    # Google OAuth URL
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={FRONTEND_URL}/auth/google/callback&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}"
    )
    
    return RedirectResponse(url=google_auth_url)

@oauth_router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}?error={error}")
    
    if not code or not state:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Missing authorization code")
    
    # Verify state parameter
    if state not in oauth_states:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": f"{FRONTEND_URL}/auth/google/callback",
                    "grant_type": "authorization_code"
                }
            )
            
            if not token_response.is_success:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Get user info from Google
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if not user_response.is_success:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            user_data = user_response.json()
            
            # Create or get user from database
            user = create_or_get_oauth_user(
                email=user_data["email"],
                full_name=user_data.get("name", ""),
                provider="google",
                provider_id=user_data["id"],
                db=db
            )
            
            # Generate JWT token using your existing auth system
            jwt_token = create_access_token(data={"sub": str(user.id)})
            
            return RedirectResponse(url=f"{FRONTEND_URL}?token={jwt_token}")
            
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Authentication failed")

@oauth_router.get("/apple")
async def apple_auth():
    """Initiate Apple OAuth flow"""
    if not APPLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Apple OAuth not configured")
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "apple", "timestamp": datetime.utcnow()}
    
    # Apple OAuth URL
    apple_auth_url = (
        f"https://appleid.apple.com/auth/authorize?"
        f"client_id={APPLE_CLIENT_ID}&"
        f"redirect_uri={FRONTEND_URL}/auth/apple/callback&"
        f"scope=name email&"
        f"response_type=code&"
        f"response_mode=form_post&"
        f"state={state}"
    )
    
    return RedirectResponse(url=apple_auth_url)

@oauth_router.post("/apple/callback")
async def apple_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Apple OAuth callback"""
    form_data = await request.form()
    code = form_data.get("code")
    state = form_data.get("state")
    error = form_data.get("error")
    
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}?error={error}")
    
    if not code or not state:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Missing authorization code")
    
    # Verify state parameter
    if state not in oauth_states:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    try:
        # Create client secret JWT for Apple
        client_secret = create_apple_client_secret()
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://appleid.apple.com/auth/token",
                data={
                    "code": code,
                    "client_id": APPLE_CLIENT_ID,
                    "client_secret": client_secret,
                    "redirect_uri": f"{FRONTEND_URL}/auth/apple/callback",
                    "grant_type": "authorization_code"
                }
            )
            
            if not token_response.is_success:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            token_data = token_response.json()
            id_token = token_data.get("id_token")
            
            # Decode Apple ID token
            user_data = jwt.decode(id_token, options={"verify_signature": False})
            
            # Get user info from form data if available (first time sign-in)
            user_info = form_data.get("user")
            full_name = ""
            if user_info:
                try:
                    user_info_dict = json.loads(user_info)
                    first_name = user_info_dict.get('name', {}).get('firstName', '')
                    last_name = user_info_dict.get('name', {}).get('lastName', '')
                    full_name = f"{first_name} {last_name}".strip()
                except:
                    full_name = ""
            
            # Create or get user from database
            user = create_or_get_oauth_user(
                email=user_data["email"],
                full_name=full_name or "User",
                provider="apple",
                provider_id=user_data["sub"],
                db=db
            )
            
            # Generate JWT token using your existing auth system
            jwt_token = create_access_token(data={"sub": str(user.id)})
            
            return RedirectResponse(url=f"{FRONTEND_URL}?token={jwt_token}")
            
    except Exception as e:
        print(f"Apple OAuth error: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=Authentication failed")

def create_apple_client_secret() -> str:
    """Create Apple client secret JWT"""
    if not APPLE_PRIVATE_KEY or not APPLE_KEY_ID or not APPLE_TEAM_ID:
        raise HTTPException(status_code=500, detail="Apple OAuth not configured properly")
    
    headers = {
        "alg": "ES256",
        "kid": APPLE_KEY_ID
    }
    
    payload = {
        "iss": APPLE_TEAM_ID,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "aud": "https://appleid.apple.com",
        "sub": APPLE_CLIENT_ID
    }
    
    return jwt.encode(payload, APPLE_PRIVATE_KEY, algorithm="ES256", headers=headers)

def create_or_get_oauth_user(email: str, full_name: str, provider: str, provider_id: str, db: Session) -> User:
    """Create or get OAuth user from database"""
    # Check if user exists by email
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        # Update OAuth provider info if needed
        if not hasattr(existing_user, 'oauth_providers') or not existing_user.oauth_providers:
            existing_user.oauth_providers = {}
        
        # If oauth_providers is a string, parse it as JSON
        if isinstance(existing_user.oauth_providers, str):
            try:
                existing_user.oauth_providers = json.loads(existing_user.oauth_providers)
            except:
                existing_user.oauth_providers = {}
        
        # Update provider info
        existing_user.oauth_providers[provider] = provider_id
        
        # If this is an OAuth user with no password, mark as OAuth user
        if not existing_user.hashed_password:
            existing_user.is_oauth_user = True
        
        # Convert back to JSON string if your model expects it
        if hasattr(existing_user, 'oauth_providers'):
            existing_user.oauth_providers = json.dumps(existing_user.oauth_providers)
        
        db.commit()
        db.refresh(existing_user)
        return existing_user
    else:
        # Create new OAuth user
        oauth_providers = json.dumps({provider: provider_id})
        
        new_user = User(
            email=email,
            full_name=full_name or "User",
            hashed_password=None,  # No password for OAuth users
            oauth_providers=oauth_providers,
            is_oauth_user=True,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

# Cleanup old state tokens (call this periodically)
def cleanup_old_states():
    """Remove expired state tokens"""
    current_time = datetime.utcnow()
    expired_states = [
        state for state, data in oauth_states.items()
        if current_time - data["timestamp"] > timedelta(minutes=10)
    ]
    
    for state in expired_states:
        del oauth_states[state]