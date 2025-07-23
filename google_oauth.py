# google_oauth.py - Google OAuth implementation
import os
import httpx
import jwt
from datetime import datetime, timezone
from fastapi import HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import User, get_db
from auth import create_access_token
import logging

logger = logging.getLogger(__name__)

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

class GoogleOAuth:
    def __init__(self):
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            logger.warning("Google OAuth credentials not configured")
    
    def get_auth_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{GOOGLE_AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GOOGLE_TOKEN_URL,
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": GOOGLE_REDIRECT_URI,
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.text}")
                    raise HTTPException(status_code=400, detail="Failed to exchange code for token")
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            raise HTTPException(status_code=400, detail="OAuth token exchange failed")
    
    async def get_user_info(self, access_token: str) -> dict:
        """Get user information from Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GOOGLE_USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"User info request failed: {response.text}")
                    raise HTTPException(status_code=400, detail="Failed to get user info")
                
                return response.json()
                
        except Exception as e:
            logger.error(f"User info error: {e}")
            raise HTTPException(status_code=400, detail="Failed to get user information")

# Global OAuth instance
google_oauth = GoogleOAuth()

# OAuth endpoints to add to your main.py
def get_google_oauth_endpoints():
    """Return Google OAuth endpoints to add to FastAPI app"""
    
    async def google_auth():
        """Initiate Google OAuth flow"""
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=501, detail="Google OAuth not configured")
        
        auth_url = google_oauth.get_auth_url()
        return RedirectResponse(url=auth_url)
    
    async def google_callback(
        code: str = Query(...),
        state: str = Query(None),
        error: str = Query(None),
        db: Session = Depends(get_db)
    ):
        """Handle Google OAuth callback"""
        
        if error:
            logger.error(f"Google OAuth error: {error}")
            return RedirectResponse(url=f"{FRONTEND_URL}?error=oauth_error")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        try:
            # Exchange code for token
            token_data = await google_oauth.exchange_code_for_token(code)
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get user info from Google
            user_info = await google_oauth.get_user_info(access_token)
            
            email = user_info.get("email")
            name = user_info.get("name", "")
            google_id = user_info.get("id")
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not provided by Google")
            
            # Check if user exists
            existing_user = db.query(User).filter(User.email == email).first()
            
            if existing_user:
                # User exists, log them in
                user = existing_user
                logger.info(f"Existing user logged in via Google: {email}")
            else:
                # Create new user
                user = User(
                    email=email,
                    full_name=name,
                    hashed_password="oauth_user",  # Placeholder for OAuth users
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                logger.info(f"New user created via Google OAuth: {email}")
            
            # Create JWT token for our app
            jwt_token = create_access_token(data={"sub": str(user.id)})
            
            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{FRONTEND_URL}?token={jwt_token}&email={email}&name={name}"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Google OAuth callback error: {e}")
            return RedirectResponse(url=f"{FRONTEND_URL}?error=oauth_failed")
    
    return {
        "google_auth": google_auth,
        "google_callback": google_callback
    }