from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from urllib.parse import quote

import msgspec
from dotenv import load_dotenv
from litestar import MediaType, Request, Response, status_codes
from litestar.config.cors import CORSConfig
from litestar.exceptions import ClientException
from litestar.exceptions.http_exceptions import ValidationException
from litestar.logging import LoggingConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.stores.memory import MemoryStore
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

# logging
LOGGING_CONFIG = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

# database
DB_HOST: str | None = os.environ.get("DB_HOST")
DB_PORT: str | None = os.environ.get("DB_PORT")
DB_NAME: str | None = os.environ.get("DB_NAME")
DB_USER: str | None = os.environ.get("DB_USER")
DB_PASSWORD: str | None = os.environ.get("DB_PASSWORD")


if DB_HOST and DB_PORT and DB_NAME and DB_USER and DB_PASSWORD:
    DATABASE_URL = f"postgresql+asyncpg://{quote(DB_USER)}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?prepared_statement_cache_size=0"
else:
    DATABASE_URL = "sqlite+aiosqlite:///db.sqlite"


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


# cors
CORS_CONFIG = CORSConfig(allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# cache
CACHE_STORE = MemoryStore()
CACHE_TIMEOUT = 3600  # seconds


# msgspec
ENCODER = msgspec.json.Encoder()
DECODER = msgspec.json.Decoder()


# rate limit
THROTTLE_CONFIG = RateLimitConfig(
    rate_limit=("minute", 100), exclude=["/schema", "/verify"]
)


# exception handler
def exception_handler(_: Request, exc: ValidationException | Exception) -> Response:
    status_code = getattr(
        exc, "status_code", status_codes.HTTP_500_INTERNAL_SERVER_ERROR
    )

    if isinstance(exc, ValidationException):
        if isinstance(exc.extra, list):
            detail = f"Validation error: {exc.extra[0]['message']}"
        else:
            detail = f"Validation error: {exc.extra}"
    else:
        detail = getattr(exc, "detail", str(exc))

    return Response(
        status_code=status_code,
        media_type=MediaType.JSON,
        content={"status": "error", "message": detail},
    )


DEBUG: bool = True if os.environ.get("DEBUG") == "True" else False
