import time
from datetime import date
from typing import Optional
from prometheus_fastapi_instrumentator import Instrumentator
import sentry_sdk
from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_versioning import VersionedFastAPI
from pydantic import BaseModel
from redis import asyncio as aioredis
from sqladmin import Admin, ModelView

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.images.router import router as router_images
from app.logger import logger
from app.pages.router import router as router_pages
from app.users.models import Users
from app.users.router import router as router_users
from app.prometheus.router import router as router_prometheus

app = FastAPI()

sentry_sdk.init(
    dsn="https://9d79e24e010af479aceedc05ab0095a6@o4507135053725696.ingest.de.sentry.io/4507135063556176",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


# app.include_router(router_auth)
# app.include_router(router_hotels)
app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_pages)
app.include_router(router_images)
app.include_router(router_prometheus)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


class HotelsSearchArgs:
    def __init__(
        self,
        location: str,
        date_from: date,
        date_to: date,
        # has_spa: Optional[bool] = None, # не отображаются типы данных в сваггере
        has_spa: bool = Query(None),  # отображаются типы данных в сваггере
        # stars: Optional[int] = Query(None, ge=1, le=5), # не отображаются типы данных в сваггере
        stars: int = Query(None, ge=1, le=5),  # отображаются типы данных в сваггере
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars


class SHotel(BaseModel):
    address: str
    name: str
    stars: int


@app.get("/hotels")
def get_hotels(search_args: HotelsSearchArgs = Depends()):
    hotels = [
        {
            "address": "ул. Гагарина, 1, Алтай",
            "name": "Super hotel",
            "stars": 5,
        }
    ]
    return search_args


app = VersionedFastAPI(
    app,
    version_format="{major}",
    prefix_format="/v{major}",
    # description='Greet users with a nice message',
    # middleware=[
    #     Middleware(SessionMiddleware, secret_key='mysecretkey')
    # ]
)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
Instrumentator().instrument(app).expose(app)


admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)


app.mount("/static", StaticFiles(directory="app/static"), "static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info("Request execution time", extra={"process_time": round(process_time, 4)})
    # response.headers["X-Process-Time"] = str(process_time)
    return response
