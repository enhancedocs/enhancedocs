import os
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    api_key = os.environ.get("ENHANCEDOCS_API_KEY")
    if api_key is None:
        return None
    token = credentials.credentials
    if api_key != token:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return token


def verify_access_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    access_token = os.environ.get("ENHANCEDOCS_ACCESS_TOKEN")
    api_key = os.environ.get("ENHANCEDOCS_API_KEY")
    if access_token is None:
        return None
    token = credentials.credentials
    if access_token != token and api_key != token:
        raise HTTPException(status_code=401, detail="Invalid Access Token")
    return token
