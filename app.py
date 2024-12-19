from litestar import Litestar, Response, get, status_codes, MediaType
from config import DEBUG
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler,
)
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from models import Base
from config import DATABASE_URL, provide_transaction
from controllers.todo import todo_router


@get("/")
async def index() -> Response:
    return Response(
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        content={"message": "Hello, World three!"},
    )


app = Litestar(
    debug=DEBUG,
    route_handlers=[index, todo_router],
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
    dependencies={"transaction": provide_transaction},
)
