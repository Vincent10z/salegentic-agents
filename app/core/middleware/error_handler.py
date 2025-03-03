from fastapi import Request
from fastapi.responses import JSONResponse
from requests import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.core.errors import AppError


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except AppError as e:
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict()
            )
        except Exception as e:
            app_error = AppError(
                message="An unexpected error occurred",
                code="INTERNAL_SERVER_ERROR",
                cause=e,
                status_code=500
            )
            return JSONResponse(
                status_code=app_error.status_code,
                content=app_error.to_dict()
            )
