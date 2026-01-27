from sqlmodel.ext.asyncio.session import AsyncSession

async def save(session: AsyncSession, obj):
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj
