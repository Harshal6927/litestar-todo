from __future__ import annotations

from typing import Sequence

from litestar import Request, Router, delete, get, post, put
from litestar.exceptions import NotFoundException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from config import CACHE_STORE, CACHE_TIMEOUT, DECODER, ENCODER
from models import TodoItem
from validators import TodoItemValidator


@get("/")
async def get_list(
    request: Request, transaction: AsyncSession, done: bool | None = None
) -> Sequence[TodoItem]:
    host = request.headers.get("host")

    # check cache
    if host:
        cached_data = await CACHE_STORE.get(host)
        if cached_data:
            request.logger.info("Cache hit in route `get_list`")
            return DECODER.decode(cached_data)

    request.logger.info("Cache miss in route `get_list`")

    # fetch data from database
    query = select(TodoItem)

    if done is not None:
        query = query.where(TodoItem.done.is_(done))

    query_result = await transaction.execute(query)

    result = []

    for item in query_result.scalars().all():
        item.__dict__.pop("_sa_instance_state")
        result.append(item.__dict__)

    # set cache
    if host:
        await CACHE_STORE.set(
            host,
            ENCODER.encode(result),
            CACHE_TIMEOUT,
        )

    return result


@post("/")
async def add_item(
    request: Request, data: TodoItemValidator, transaction: AsyncSession
) -> TodoItem:
    request.logger.info(f"Adding todo item: {data}")

    transaction.add(TodoItem(task=data.task, done=data.done))
    await transaction.flush()
    new_item = await transaction.execute(
        select(TodoItem).order_by(TodoItem.id.desc()).limit(1)
    )
    new_item = new_item.scalar_one()

    # reset cache
    await CACHE_STORE.delete_all()

    return new_item


@put("/{id:int}")
async def update_item(
    id: int, request: Request, data: TodoItemValidator, transaction: AsyncSession
) -> TodoItem:
    request.logger.info(f"Updating todo item with id {id}: {data}")

    query = select(TodoItem).where(TodoItem.id == id)
    todo_item = await transaction.execute(query)

    try:
        todo_item = todo_item.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"Todo item with id {id} not found") from e

    todo_item.task = data.task
    todo_item.done = data.done

    # reset cache
    await CACHE_STORE.delete_all()

    return todo_item


@delete("/{id:int}")
async def delete_item(id: int, transaction: AsyncSession) -> None:
    query = select(TodoItem).where(TodoItem.id == id)
    todo_item = await transaction.execute(query)

    try:
        todo_item = todo_item.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"Todo item with id {id} not found") from e

    await transaction.delete(todo_item)

    # reset cache
    await CACHE_STORE.delete_all()


@get("/{id:int}")
async def get_item(id: int, transaction: AsyncSession) -> TodoItem:
    query = select(TodoItem).where(TodoItem.id == id)
    todo_item = await transaction.execute(query)

    try:
        todo_item = todo_item.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"Todo item with id {id} not found") from e

    return todo_item


todo_router = Router(
    path="/todo",
    route_handlers=[get_list, add_item, update_item, delete_item, get_item],
)
