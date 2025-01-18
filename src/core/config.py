from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR: Path = Path(__file__).parent.parent.parent


class DBConfig(BaseModel):
    user: str = "user"
    password: str = "password"
    host: str = "localhost"
    port: int = 5432
    name: str = "db_name"
    provider: str = "postgresql+asyncpg"

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self: Self) -> str:
        return f"{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class GunicornConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 4
    timeout: int = 900
    loglevel: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"


class FastApiConfig(BaseModel):
    title: str = "FastAPI base app"
    description: str = "FastAPI base app description"
    version: str = "0.1.0"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    log_requests: bool = True


class CorsConfig(BaseModel):
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[
        Literal[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "HEAD",
            "OPTIONS",
            "TRACE",
            "CONNECT",
            "*",
        ]
    ] = ["*"]
    allow_headers: list[str] = ["*"]


class DevConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True


class Settings(BaseSettings):
    db: DBConfig = DBConfig()
    gunicorn: GunicornConfig = GunicornConfig()
    fastapi: FastApiConfig = FastApiConfig()
    cors: CorsConfig = CorsConfig()
    dev: DevConfig = DevConfig()

    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


settings = Settings()
