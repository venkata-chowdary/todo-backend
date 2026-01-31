from sqlmodel import SQLModel, Field
import uuid

class Todo(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    completed: bool = False
    user_id: uuid.UUID = Field(foreign_key="user.id")