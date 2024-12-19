from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class TodoItem(Base):
    __tablename__ = "todo_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    task: Mapped[str] = mapped_column(nullable=False)
    done: Mapped[bool] = mapped_column(nullable=False, default=False)
