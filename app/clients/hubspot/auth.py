from typing import Optional, Dict
import aiohttp
from datetime import datetime, timedelta
from fastapi import HTTPException

class HubspotAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://app.hubspot.com/oauth/authorize"
        self.token_url = "https://api.hubapi.com/oauth/v1/token"

    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "contacts content",  # Add required scopes
            "state": state
        }
        return f"{self.auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

    async def exchange_code(self, code: str) -> Dict:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to exchange code")
                return await response.json()

    async def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token."""
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to refresh token")
                return await response.json()