import uvicorn

from src.bootstrap import create_app
from src.core.config import settings


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.dev.host,
        port=settings.dev.port,
        reload=settings.dev.reload,
    )
