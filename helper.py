from sqlmodel.ext.asyncio.session import AsyncSession

async def save(session: AsyncSession, obj):
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

import hashlib

def generate_task_hash(title: str, description: str | None) -> str:
    normalized = f"{title.strip().lower()}::{(description or '').strip().lower()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
