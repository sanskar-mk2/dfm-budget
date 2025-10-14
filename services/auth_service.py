from datetime import timedelta, datetime, timezone
import jwt
import bcrypt
from sqlmodel import Session
from db.dfm_reflect import Users
from constants import ALGORITHM
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str, db: Session) -> Users | None:
    from sqlmodel import select

    user = db.exec(select(Users).where(Users.username == username)).first()
    if not user:
        return None
    if not bcrypt.checkpw(
        password.encode("utf-8"), user.hashed_password.encode("utf-8")
    ):
        return None
    return user
