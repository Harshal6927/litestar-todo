from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from sqlalchemy.exc import IntegrityError
from litestar.exceptions import ClientException
from litestar import status_codes
import os
from dotenv import load_dotenv

load_dotenv()


DEBUG: bool = True if os.environ.get("DEBUG") == "True" else False


DATABASE_URL = "sqlite+aiosqlite:///db.sqlite"


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
