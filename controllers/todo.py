from __future__ import annotations

from typing import Sequence

from litestar import (MediaType, Request, Response, Router, delete, get, post,
                      put, status_codes)
from litestar.exceptions import ClientException, NotFoundException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from config import CACHE_STORE, CACHE_TIMEOUT, ENCODER
from models import TodoItem
from validators import TodoItemValidator


@get("/")
async def get_list(
    transaction: AsyncSession, done: bool | None = None
) -> Sequence[TodoItem]:
    query = select(TodoItem)
    if done is not None:
        query = query.where(TodoItem.done.is_(done))

    result = await transaction.execute(query)
    return result.scalars().all()


@post("/")
async def add_item(data: TodoItemValidator, transaction: AsyncSession) -> TodoItem:
    transaction.add(TodoItem(task=data.task, done=data.done))
    await transaction.flush()
    new_item = await transaction.execute(
        select(TodoItem).order_by(TodoItem.id.desc()).limit(1)
    )
    new_item = new_item.scalar_one()
    return new_item


@put("/{id:int}")
async def update_item(
    id: int, data: TodoItemValidator, transaction: AsyncSession
) -> TodoItem:
    query = select(TodoItem).where(TodoItem.id == id)
    todo_item = await transaction.execute(query)

    try:
        todo_item = todo_item.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"Todo item with id {id} not found") from e

    todo_item.task = data.task
    todo_item.done = data.done
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
