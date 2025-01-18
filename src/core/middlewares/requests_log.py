import json
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import Callable, Awaitable, Any

from fastapi.responses import Response
from fastapi.requests import Request
from starlette.datastructures import QueryParams
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import BASE_DIR


class RequestsLogMiddleware(BaseHTTPMiddleware):
    """
    My workaround of the issue when access_log_format is not working with
    UvicornWorker worker_class with gunicorn, so we can't use the following
    syntax: https://docs.gunicorn.org/en/latest/settings.html#access-log-format
    """

    LOGGER: logging.Logger = logging.Logger("requests", level=logging.INFO)
    FORMATTER: logging.Formatter = logging.Formatter("[%(asctime)s] %(message)s")
    HANDLER: RotatingFileHandler = RotatingFileHandler(
        f"{BASE_DIR}/logs/requests.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
    )
    HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(HANDLER)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        body: bytes = await request.body()
        query: QueryParams = request.query_params
        start_time: float = time.perf_counter()
        response: Response = await call_next(request)

        content_type: str = request.headers.get("content-type", "")
        if body and content_type.startswith("application/json"):
            try:
                body_content: Any = json.loads(body)
                body_str: str = json.dumps(body_content)
            except json.JSONDecodeError:
                body_str = "Invalid JSON"
        else:
            body_str = f"Non-JSON body, Content-Type: {content_type}"

        response_time: str = f"{time.perf_counter() - start_time:.5f}"

        self.LOGGER.info(
            "%s %s%s%s | %d | Response Time: %s",
            request.method,
            request.url.path,
            f" | QueryParams: {query}" if query else "",
            f" | Body: {body_str}" if body else "",
            response.status_code,
            response_time,
        )

        return response
