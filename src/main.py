import logging
from contextlib import asynccontextmanager

import aiohttp
from redis.asyncio import Redis
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from asgi_correlation_id import CorrelationIdMiddleware

from src import http_client, cache
from src.config import settings
from src.ping import router as ping_router
from src.loggers import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    cache.cache = Redis(host=settings.redis_host, port=settings.redis_port)
    http_client.session = aiohttp.ClientSession()
    yield
    await http_client.session.close()
    await cache.cache.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(ping_router, tags=["ping"])


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
