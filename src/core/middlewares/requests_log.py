import time
import logging
from logging.handlers import RotatingFileHandler

from fastapi import requests
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import BASE_DIR


class RequestsLogMiddleware(BaseHTTPMiddleware):
    """
    My workaround of the issue when access_log_format is not working with
    UvicornWorker worker_class with gunicorn, so we can't use the following
    syntax: https://docs.gunicorn.org/en/latest/settings.html#access-log-format
    """

    LOGGER = logging.Logger("requests", level=logging.INFO)
    FORMATTER = logging.Formatter("[%(asctime)s] %(message)s")
    HANDLER = RotatingFileHandler(
        f"{BASE_DIR}/logs/requests.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
    )
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)

    async def dispatch(self, request: requests.Request, call_next):
        body = await request.body()
        query = request.query_params
        start_time = time.perf_counter()
        response = await call_next(request)

        log_time = f"{time.perf_counter() - start_time:.5f}"

        self.LOGGER.info(
            "%s %s%s%s | %d | Response Time: %s",
            request.method,
            request.url.path,
            f" | QueryParams: {query}" if query else "",
            f" | Body: {body.decode()}" if body else "",
            response.status_code,
            log_time,
        )

        return response
