from fastapi import APIRouter
from ..schemas.signin_input import SigninInput
from ..services.database import get_db
from ..models.users_class import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException
from ..auth.passlib_setup import pwd_context
from ..auth.jwt import create_access_token, access_token_cookie
from fastapi import Response

router = APIRouter()

@router.post("/signin")
async def signin(response: Response, new: SigninInput, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == new.email))
    same_user = result.scalar_one_or_none()
    if same_user:
        raise HTTPException(status_code=400, detail="User already exists pls login")
    hash_password = pwd_context.hash(new.password[:72])
    adds = User(name=new.name, email=new.email, password=hash_password)
    try:
        db.add(adds)
        await db.commit()
        await db.refresh(adds)
        token = create_access_token({"id": adds.id , "email": adds.email})
        access_token_cookie(response, token)
        return {"message": "User created successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")


   