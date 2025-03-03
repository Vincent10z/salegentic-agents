# app/routes/v1/health/endpoints.py
import http

from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()


async def health_check():
    return {"status": http.HTTPStatus.OK}
