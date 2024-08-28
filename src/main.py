import logging
from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src import cache, http_client
from src.config import settings
from src.loggers import setup_logging
from src.ping import router as ping_router
from src.place.router import router as place_router
from src.watch.router import router as watch_router

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
app.include_router(place_router, prefix="/api/v1/places", tags=["place"])
app.include_router(watch_router, prefix="/api/v1/watches", tags=["watch"])


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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=logging.DEBUG,
        reload=True,
    )
