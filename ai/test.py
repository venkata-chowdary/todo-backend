import asyncio
from app.ai.service import analyze_task

async def test():
    res = await analyze_task(
        title="Prepare for system design interview",
        description="Focus on caching and rate limiting"
    )
    print(res)

asyncio.run(test())
