from src.core.config import BASE_DIR, settings


command: str = str(BASE_DIR / ".venv/bin/gunicorn")
pythonpath: str = str(BASE_DIR)
bind: str = f"{settings.gunicorn.host}:{settings.gunicorn.port}"
workers: int = settings.gunicorn.workers
worker_class: str = "uvicorn.workers.UvicornWorker"

accesslog: str | None = None
errorlog: str = f"{BASE_DIR}/logs/gunicorn.error.log"

capture_output = True
loglevel: str = settings.gunicorn.loglevel
