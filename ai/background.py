from app.models import Todo
from app.ai.service import analyze_task
from uuid import UUID
from app.db import async_session_factory

async def save_analysed_data(todo_id:UUID, title: str, description: str ):
    async with async_session_factory() as session:    
        print("Background AI task started for todo:", todo_id)

        exsisting_todo=await session.get(Todo, todo_id)
        if not exsisting_todo:
            print("failed to fetch todo:{todo_id}")
            return
                
        ai_result=await analyze_task(title, description)
        exsisting_todo.category = ai_result.category
        exsisting_todo.priority = ai_result.priority
        exsisting_todo.suggested_due_date = ai_result.suggested_due_date

        await session.commit()
