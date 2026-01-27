from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func, asc, desc

from schemas import TodoCreate, TodoUpdate
from models import Todo

from database_demo import todos_db
from helper import save
import uuid

from typing import Optional
from db import get_session

import logging
from uuid import UUID
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router=APIRouter()

@router.post("/todos", status_code=201,  response_model=Todo)
async def create_todo(
    todo: TodoCreate, 
    description="to create todo", 
    session: AsyncSession= Depends(get_session)
    ):
    
    new_todo = Todo(**todo.dict())
    logger.info(f"new todo created.")
    return await save(session ,new_todo)


@router.get("/todos/{todo_id}", status_code=200, response_model=Todo)
async def get_todo(todo_id: UUID = Path(..., description="The ID of the todo to retrieve"), session: AsyncSession=Depends(get_session)):
    todo=await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="not todo existed")
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
    limit: int = Query(5, ge=1, lt=10, description="To get all todos"),
    offset: int = Query(0, ge=0, description="offset for pagination"),
    completed: Optional[bool]= Query(None, description="filter by completed status"),
    sort_by: str = Query("id", description="Sort field: id/title"),
    order: str = Query("asc", description="Sort order: asc/desc"),
    session: AsyncSession=Depends(get_session)
    ):
    query=select(Todo)
    sort_order = asc if order == "asc" else desc

    if completed is not None:
        query=query.where(Todo.completed==True)

    query = query.order_by(sort_order(getattr(Todo, sort_by)))

    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    todos = result.scalars().all()
    
    total_query = select(func.count()).select_from(Todo)
    if completed is not None:
        total_query = total_query.where(Todo.completed == completed)

    total_result = await session.execute(total_query)
    return {"total": total_result.scalar(),"limit": limit,"offset": offset,"data": result}           