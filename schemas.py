from pydantic import BaseModel, Field
from typing import Optional, Annotated
from uuid import UUID

class TodoBase(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=10, description="todo title")]
    description: Annotated[Optional[str], Field(None, max_length=200, description="todo description")]
    completed: Annotated[bool, Field(False, description="todo completion status")]
    
class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: UUID