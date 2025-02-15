# app/routes/v1/health/endpoints.py
import http

from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": http.HTTPStatus.OK}
