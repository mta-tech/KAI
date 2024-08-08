from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
