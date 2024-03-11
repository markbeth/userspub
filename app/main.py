from app.config import settings
from app.users.router import router as router_users
from app.logger import logger
from app.database import async_engine
from app.admin.views import UserAdmin

import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from fastapi_versioning import VersionedFastAPI, version
from sqladmin import Admin

from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from time import time
import sentry_sdk


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")

    yield
    
    
app = FastAPI(
    title="Users API doc, mkbeth",
    version="0.1.0",
    root_path="/api",
    lifespan=lifespan
)
app.include_router(router_users)


@app.get("/")
def root():
    return {"Users microservice"}


@app.middleware("http")
async def add_process(
    request: Request,
    call_next
):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    logger.info("Request execution time", extra={
        "process_time": round(process_time, 4)
    })
    return response

app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    description="v1"
)

admin = Admin(app, async_engine)

admin.add_view(UserAdmin)


origins = [
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://0.0.0.0:8001",
    "http://0.0.0.0:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                    "Access-Authorization"]
)


sentry_sdk.init(
    dsn=settings.CENTRY,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    enable_tracing=True
) 

