from app.models import Todo
from app.ai.service import analyze_task
from uuid import UUID
from app.db import async_session_factory
from redis.asyncio import Redis
import json
redis_client = Redis(host='localhost', port=6379, db=0)

async def save_analysed_data(todo_id:UUID, title: str, description: str, cache_key: str ):
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
        
        print("caching todo to redis")
        await redis_client.set(
            cache_key,
            json.dumps({
                "category": ai_result.category,
                "priority": ai_result.priority,
                "suggested_due_date": (
                    ai_result.suggested_due_date.isoformat()
                    if ai_result.suggested_due_date else None
                )
            }),
            ex=60 * 60 * 24  # 24 hours TTL
        )

        await session.commit()
