# app/routes/v1/health/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()

@router.get("/")
async def health_check():
    return {"status": "healthy"}