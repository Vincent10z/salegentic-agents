from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Dependency function to get the current authenticated user from the bearer token.
    Returns the user data if the token is valid.
    """
    try:
        # Here you would typically validate the token against your auth service
        # For now, we'll just return a basic user dict
        return {
            "id": "user-id",  # You would get this from token validation
            "token": credentials.credentials
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )