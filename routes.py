from fastapi import APIRouter, HTTPException, Path, Query, Depends, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func, asc, desc
from app.schemas import TodoCreate, TodoUpdate, NLTodoRequest, TodoCreateResponse
from app.auth.dependencies import get_current_user
from app.models import Todo
from app.helper import save
from typing import Optional
from app.db import get_session
from app.ai.background import save_analysed_data
from app.ai.service import parse_nl_todo
from app.helper import generate_task_hash
from datetime import date
from app.ai.background import store_vector_emd
import logging
import json
from uuid import UUID
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router=APIRouter()


from redis.asyncio import Redis
redis_client = Redis(host='localhost', port=6379, db=0)

@router.post("/todos", status_code=201,  response_model=TodoCreateResponse)
async def create_todo(
    todo: TodoCreate, 
    background_tasks : BackgroundTasks,
    description="to create todo", 
    user = Depends(get_current_user),
    session: AsyncSession= Depends(get_session),
    ):
    
    #check duplicate
    duplicate=await check_duplicate(todo.title, todo.description)
    
    #create todo
    new_todo = Todo(
        user_id=user.id,
        **todo.dict(),
        ai_generated=False
    )

    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)
    
    task_hash=generate_task_hash(title=todo.title, description=todo.description)
    key=f"ai:task_analysis:{task_hash}"
    cached_todo=await redis_client.get(key)

    if cached_todo:
        print("getting ticket data from cached memeory")
        ai_data = json.loads(cached_todo)
        
        new_todo.priority=ai_data['priority']
        if ai_data["suggested_due_date"]:
            new_todo.suggested_due_date = date.fromisoformat(ai_data["suggested_due_date"])
        else:
            new_todo.suggested_due_date = None        
        new_todo.category=ai_data['category']
        
        await session.commit()
    else:
        background_tasks.add_task(
        save_analysed_data,
        new_todo.id,
        new_todo.title,
        new_todo.description,
        key
        )
    logger.info(f"new todo created.")
    
    
    background_tasks.add_task(
    store_vector_emd,
    new_todo.title,
    new_todo.description,
    new_todo.id,
    )

    return {
        "todo": new_todo,
        "duplicate_warning": duplicate
    }

# @router.post("/todos/bulk", status_code=201)
# async def create_multiple_todos(
#     count: int = 100,
#     session: AsyncSession = Depends(get_session)
# ):
#     todos_created = []

#     for i in range(1, count + 1):
#         todo_obj = TodoCreate(title=f"Todo {i}", description=f"Auto generated todo {i}")
#         new_todo = Todo(**todo_obj.dict())
#         saved = await save(session, new_todo)  # your existing save logic
#         todos_created.append(saved)

#     return {"message": f"{count} todos created.", "todos": todos_created}

from app.ai.search import semantic_search
@router.get("/todos/semantic-search")
async def semantic_search_todos(
    query: str,
    limit: int = 5
):
    results = await semantic_search(query, limit)
    return results

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


@router.post("/todos/nl", status_code=201, response_model=Todo)
async def create_nl_todo(
    payload: NLTodoRequest,
    background_tasks : BackgroundTasks,
    description= "to create todo using natural language",
    user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    result=await parse_nl_todo(user_input=payload.input)
    
    new_todo= Todo(
        user_id = user.id,
        ai_generated=True,
        title = result.title,
        description = result.description
    )
    
    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)
    
    task_hash=generate_task_hash(title=new_todo.title, description=new_todo.description)
    key=f"ai:task_aanalysis:{task_hash}"
    background_tasks.add_task(
        save_analysed_data,
        new_todo.id,
        new_todo.title,
        new_todo.description,
        key
    )
    
    logger.info(f"new todo created.")

    background_tasks.add_task(
        store_vector_emd,
        new_todo.title,
        new_todo.description,
        new_todo.id,
    )
    return new_todo

from app.ai.embeddings import generate_embedding
from app.ai.vector_store import collection
from app.ai.duplicate import check_duplicate

from uuid import uuid4
@router.post("/test")
async def test_add_embedding():
    
    result=await check_duplicate()    
    print(result)
