import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from src.config import settings


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    return await call_next(request)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.error("Exception has occurred when handled request to %s: %s", request.url, exc)
    return ORJSONResponse(status_code=500, content={"detail": "internal server error"})
