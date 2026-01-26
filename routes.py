from fastapi import APIRouter, HTTPException 
from schemas import TodoCreate, Todo
from database import todos_db
import uuid
import logging

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