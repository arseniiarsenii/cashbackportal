from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, Response

from cashbackportal.core import auth, controllers, models

from .. import templates
from ..dependencies import get_db_session, get_user
from . import schemas

router = APIRouter(tags=["Users"])


@router.post("/sign-up")
async def sign_up(
    response: Response, user_details: schemas.SignUpRequest, db_session: AsyncSession = Depends(get_db_session)
) -> schemas.TokenResponse:
    existing_user = await controllers.get_user_by_email(db_session, user_details.email)
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    user = await controllers.create_user(
        db_session,
        email=user_details.email,
        password=user_details.password,
        name=user_details.name,
    )
    token, expires_at = auth.create_access_token(user)
    response.set_cookie(key="access_token", value=token, httponly=True, expires=expires_at)
    return schemas.TokenResponse(access_token=token, expires_at=expires_at)


@router.get("/sign-up")
async def get_signup_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/sign-in")
async def sign_in(
    response: Response, form_data: schemas.SignInRequest, db_session: AsyncSession = Depends(get_db_session)
) -> schemas.TokenResponse:
    user = await auth.authenticate_user(db_session, email=form_data.email, password=form_data.password)
    token, expires_at = auth.create_access_token(user)
    response.set_cookie(key="access_token", value=token, httponly=True, expires=expires_at)
    return schemas.TokenResponse(access_token=token, expires_at=expires_at)


@router.get("/sign-in")
async def get_signin_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("signin.html", {"request": request})


@router.get("/sign-out")
async def sign_out() -> RedirectResponse:
    response = RedirectResponse("/")
    response.delete_cookie("access_token")
    return response


@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_user)) -> schemas.UserResponse:
    return schemas.UserResponse.model_validate(current_user, from_attributes=True)
