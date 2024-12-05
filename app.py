from __future__ import annotations

import datetime

from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import \
    autocommit_before_send_handler
from litestar import Litestar, MediaType, Request, Response, get, status_codes
from litestar.contrib.sqlalchemy.plugins import (SQLAlchemyAsyncConfig,
                                                 SQLAlchemyPlugin)

from config import (CACHE_STORE, CORS_CONFIG, DATABASE_URL, DEBUG,
                    LOGGING_CONFIG, THROTTLE_CONFIG, exception_handler,
                    provide_transaction)
from controllers.todo import todo_router
from models import Base


@get("/")
async def index() -> Response:
    return Response(
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        content="Hello, world!",
    )


# cache cleanup
async def after_response(request: Request) -> None:
    now = datetime.datetime.now(datetime.UTC)
    last_cleared = request.app.state.get("store_last_cleared", now)
    if datetime.datetime.now(datetime.UTC) - last_cleared > datetime.timedelta(
        seconds=30
    ):
        await CACHE_STORE.delete_expired()
    app.state["store_last_cleared"] = now


app = Litestar(
    debug=DEBUG,
    route_handlers=[index, todo_router],
    logging_config=LOGGING_CONFIG,
    cors_config=CORS_CONFIG,
    dependencies={"transaction": provide_transaction},
    plugins=[
        SQLAlchemyPlugin(
            SQLAlchemyAsyncConfig(
                connection_string=DATABASE_URL,
                metadata=Base.metadata,
                create_all=True,
                before_send_handler=autocommit_before_send_handler,
            )
        )
    ],
    after_response=after_response,
    middleware=[THROTTLE_CONFIG.middleware],
    exception_handlers={Exception: exception_handler},
)
