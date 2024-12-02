from __future__ import annotations

from typing import Annotated

from msgspec import Meta, Struct


class TodoItemValidator(Struct):
    task: Annotated[str, Meta(min_length=1, max_length=255)]
    done: bool = False
