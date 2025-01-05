from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware

from src.db.db_service import db_service
from src.core.middlewares import RequestsLogMiddleware
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_service.dispose()


app: FastAPI = FastAPI(
    title=settings.fastapi.title,
    description=settings.fastapi.description,
    version=settings.fastapi.version,
    docs_url=settings.fastapi.docs_url,
    redoc_url=settings.fastapi.redoc_url,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors.allow_origins,
            allow_credentials=settings.cors.allow_credentials,
            allow_methods=settings.cors.allow_methods,
            allow_headers=settings.cors.allow_headers,
        )
    ],
)

if settings.fastapi.log_requests:
    app.add_middleware(RequestsLogMiddleware)


@app.get("/status")
async def check_app_status():
    """
    Check app status
    """
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.dev.host,
        port=settings.dev.port,
        reload=settings.dev.reload,
    )
