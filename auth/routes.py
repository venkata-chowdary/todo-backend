from fastapi import APIRouter, HTTPException, Path, Query, Depends
from app.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select, func, asc, desc
from app.auth.security import hash_password
from app.auth.models import User
from app.auth.schemas import UserCreate, UserResponse, UserLogin
from app.auth.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post('/register',response_model=UserResponse, status_code=201)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    exsisting_user=select(User).where(User.email==user.email)
    result=await session.exec(exsisting_user)
    
    if result.first():
        raise HTTPException(400, "Email already registered")
    
    new_user=User(email=user.email, hashed_password=hash_password(user.password))
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user
    
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(User).where(User.email == form_data.username)
    result = await session.exec(stmt)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }
