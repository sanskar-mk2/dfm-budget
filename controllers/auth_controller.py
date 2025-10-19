from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from db.core import get_readonly_session
from sqlmodel import Session
from db.dfm_reflect import Salesperson
from fastapi import HTTPException
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from constants import ACCESS_TOKEN_EXPIRE_MINUTES, SUPERADMIN, ADMIN
from services.auth_service import authenticate_user, create_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(
    tags=["auth"],
)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_readonly_session),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Check if user is admin
    is_admin = user.salesman_id == SUPERADMIN or user.salesman_id is ADMIN
    is_superadmin = user.salesman_id == SUPERADMIN
    print(user.salesman_id, is_admin, is_superadmin)

    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": is_admin,
        "is_superadmin": is_superadmin,
    }

    if user.salesman_id and not is_admin:
        salesperson = db.exec(
            select(Salesperson).where(Salesperson.salesman_no == user.salesman_id)
        ).first()
        response["salesperson"] = salesperson
    return response
