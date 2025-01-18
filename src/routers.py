from fastapi import FastAPI

from src.apps.v1 import router as v1_router


def apply_routers(app: FastAPI) -> FastAPI:
    app.include_router(v1_router)

    return app
