from fastapi import APIRouter, HTTPException, Path, Query
from schemas import TodoCreate, Todo
from database import todos_db
import uuid
from typing import Optional

import logging
from uuid import UUID
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router=APIRouter()

@router.post("/todos", status_code=201,  response_model=Todo)
async def create_todo(todo: TodoCreate, description="to create todo"):
    todo_id=uuid.uuid4()
    new_todo= Todo(id= todo_id, **todo.dict())
    prev_length=len(todos_db)
    todos_db.append(new_todo)
    
    if prev_length + 1 !=len(todos_db):
        raise HTTPException(status_code=500, detail="Failed to add todo")
    logger.info(f"Creating todo with id: {todo_id}")
    return new_todo


@router.get("/todos/{todo_id}", status_code=200, response_model=Todo)
async def get_todo(todo_id: UUID = Path(..., description="The ID of the todo to retrieve")):
    for todo in todos_db:
        if todo.id and todo.id==todo_id:
            return todo
    raise HTTPException(status_code=404, detail="not todo existed")

@router.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: UUID = Path(..., description="id of the todo to update"),
    todo_data: Todo = None
):
    for index, todo in enumerate(todos_db):
        if todo.id == todo_id:
            todo.title = todo_data.title
            todo.description = todo_data.description
            todo.completed = todo_data.completed
            
            todos_db[index] = todo
            return todo

    raise HTTPException(status_code=404, detail="Todo not found")

@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID = Path(..., description="ID of todo to delete")):
    for index, todo in enumerate(todos_db):
        if todo_id==todo.id:
            deleted_todo=todos_db.pop(index)
            return deleted_todo
        
    raise HTTPException(status_code=404, detail="Todo not found to delete")


@router.get("/todos", status_code=200)
async def get_todos(
    limit: int = Query(5, ge=1, lt=10, description="To get all todos"),
    offset: int = Query(0, ge=0, description="offset for pagination"),
    completed: Optional[bool]= Query(None, description="filter by completed status"),
    sort_by: str = Query("id", description="Sort field: id/title"),
    order: str = Query("asc", description="Sort order: asc/desc")
    ):
    data=todos_db
    if completed is not None:
        data=[todo for todo in data if todo.completed==completed]
    reverse=(order=='desc')
    data = sorted(data, key=lambda x: getattr(x, sort_by), reverse=reverse)
    result=data[offset: offset+limit]
    
    return {"total": len(todos_db),"limit": limit,"offset": offset,"data": result}


@router.patch("/todos/{todo_id}/status", response_model=Todo)
async def update_todo_status(todo_id: UUID):
    for index, todo in enumerate(todos_db):
        if todo.id==todo_id:
            todo.completed=True
            return todo
    return HTTPException(404, detail="Todo not found")
            