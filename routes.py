from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func, asc, desc
from schemas import TodoCreate, TodoUpdate
from models import Todo
from helper import save
from typing import Optional
from db import get_session

import logging
from uuid import UUID
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router=APIRouter()


from redis.asyncio import Redis
redis_client = Redis(host='localhost', port=6379, db=0)

@router.post("/todos", status_code=201,  response_model=Todo)
async def create_todo(
    todo: TodoCreate, 
    description="to create todo", 
    session: AsyncSession= Depends(get_session)
    ):
    
    new_todo = Todo(**todo.dict())
    logger.info(f"new todo created.")
    return await save(session ,new_todo)

@router.post("/todos/bulk", status_code=201)
async def create_multiple_todos(
    count: int = 100,
    session: AsyncSession = Depends(get_session)
):
    todos_created = []

    for i in range(1, count + 1):
        todo_obj = TodoCreate(title=f"Todo {i}", description=f"Auto generated todo {i}")
        new_todo = Todo(**todo_obj.dict())
        saved = await save(session, new_todo)  # your existing save logic
        todos_created.append(saved)

    return {"message": f"{count} todos created.", "todos": todos_created}

import json

@router.get("/todos/{todo_id}", status_code=200, response_model=Todo)
async def get_todo(todo_id: UUID = Path(..., description="The ID of the todo to retrieve"), session: AsyncSession=Depends(get_session)):
    key=f"todo:{todo_id}"
    cached=await redis_client.get(key)
    
    if cached:
        logger.info("returning data from redis")
        todo_data=json.loads(cached)
        return Todo(**todo_data)
    
    todo=await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="not todo existed")
    todo_dict = todo.dict()
    for k, v in todo_dict.items():
        if isinstance(v, UUID):
            todo_dict[k] = str(v)

    await redis_client.set(key, json.dumps(todo_dict), ex=60)
    logger.info("Saving Todo to Redis Cache")
    return todo


@router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID = Path(..., description="ID of todo to delete"), session: AsyncSession=Depends(get_session)):
    exsisting_todo=await session.get(Todo, todo_id)
    if not exsisting_todo:
        raise HTTPException(status_code=404, detail="Todo not found to delete")
    await session.delete(exsisting_todo)
    await session.commit()
    return {"ok": True}        


@router.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: UUID = Path(..., description="id of the todo to update"),
    todo: TodoUpdate = None,
    session: AsyncSession=Depends(get_session)
):
    exsisting_todo=await session.get(Todo, todo_id)
    if not exsisting_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_data= todo.model_dump(exclude_unset=True)
    for key, value in todo_data.items():
        setattr(exsisting_todo, key, value)
    await session.commit()
    await session.refresh(exsisting_todo)
    return exsisting_todo

@router.patch("/todos/{todo_id}/status", response_model=Todo)
async def update_todo_status(todo_id: UUID,session: AsyncSession=Depends(get_session)):
    exsisting_todo=await session.get(Todo, todo_id)
    if not exsisting_todo:
        return HTTPException(404, detail="Todo not found")
    setattr(exsisting_todo, 'completed', True)
    await session.commit()
    await session.refresh(exsisting_todo)
    return exsisting_todo
    
@router.get("/todos", status_code=200)
async def get_todos(
    limit: int = Query(5, ge=1, lt=101, description="To get all todos"),
    offset: int = Query(0, ge=0, description="offset for pagination"),
    completed: Optional[bool]= Query(None, description="filter by completed status"),
    sort_by: str = Query("id", description="Sort field: id/title"),
    order: str = Query("asc", description="Sort order: asc/desc"),
    session: AsyncSession=Depends(get_session)
    ):
    
    key = f"todos:{limit}:{offset}:{completed}:{sort_by}:{order}"
    cached = await redis_client.get(key)
    if cached:
        logger.info("Returning TODOS from Redis Cache")
        return eval(cached)

    
    query=select(Todo)
    sort_order = asc if order == "asc" else desc

    if completed is not None:
        query=query.where(Todo.completed==True)

    query = query.order_by(sort_order(getattr(Todo, sort_by)))

    query = query.offset(offset)
    result = await session.execute(query)
    todos = result.scalars().all()
    
        
    total_query = select(func.count()).select_from(Todo)
    if completed is not None:
        total_query = total_query.where(Todo.completed == completed)

    total_result = await session.execute(total_query)
    response_data= {"total": total_result.scalar(),"limit": limit,"offset": offset,"data": todos}           
    
    await redis_client.set(key, str(response_data), ex=600)
    logger.info("Saving TODOS response to Redis Cache")
    return response_data