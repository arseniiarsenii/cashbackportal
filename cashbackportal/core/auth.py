from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from cashbackportal import config

from . import models
from .controllers import get_user_by_email
from .utils import utc_now

ALGORITHM = "HS256"
ACCESS_TOKEN_TTL_MIN = 720


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(db_session: AsyncSession, email: str, password: str) -> models.User:
    user = await get_user_by_email(db_session, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {email} not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    if user.status == models.UserStatus.inactive:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def create_access_token(user: models.User) -> tuple[str, datetime]:
    expires_at = utc_now() + timedelta(minutes=ACCESS_TOKEN_TTL_MIN)
    payload = {"sub": user.email, "exp": expires_at}
    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token, expires_at


async def get_current_user(db_session: AsyncSession, jwt_token: str) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(jwt_token, config.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(db_session, email)
    if user is None:
        raise credentials_exception
    return user
