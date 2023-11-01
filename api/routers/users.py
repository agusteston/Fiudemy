from fastapi import APIRouter, HTTPException

from auth import AuthHandler
from db import engine
from sqlmodel import Session
from models import UserInput, User, UserLogin
from repositories.user_repository import select_all_users, find_user, update_user
from dependencies import UserDependency

user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post('/registration', status_code=201, tags=['users'],
                  description='Register new user')
def register(user: UserInput):
    users = select_all_users()
    if any(x.username == user.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_pwd = auth_handler.get_password_hash(user.password)
    with Session(engine) as session:
        u = User(username=user.username, password=hashed_pwd, email=user.email)
        session.add(u)
        session.commit()
        session.refresh(u)
        return u


@user_router.post('/login', tags=['users'])
def login(user: UserLogin):
    user_found = find_user(user.username)
    if not user_found:
        raise HTTPException(status_code=401,
                            detail='Invalid username and/or password')
    verified = auth_handler.verify_password(user.password, user_found.password)
    if not verified:
        raise HTTPException(status_code=401,
                            detail='Invalid username and/or password')
    token = auth_handler.encode_token(user_found.username)
    return {'token': token}


@user_router.get('/users/me', tags=['users'])
def get_current_user(user: UserDependency )):
    return user


@user_router.get('/users/about_me', tags=['users'])
def get_current_user_about_me(user: UserDependency ):
    return user.about_me


@user_router.put('/update-about-me', tags=['users'])
def update_about_me(about_me: str, user: UserDependency):
    user_found = find_user(user.username)
    user_found.about_me = about_me
    update_user(user_found)
    return {'message': 'About me updated successfully'}
