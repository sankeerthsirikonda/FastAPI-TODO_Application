from fastapi import APIRouter,Request
from pydantic import BaseModel
from ..models import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,HTTPException,Path,status
from ..database import engine,SessionLocal
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import timedelta,datetime,timezone
from fastapi.templating import Jinja2Templates

router=APIRouter(prefix='/auth',tags=['auth'])

SECRET_KEY='9f3c7e4b8a1d6e2c4f9a0b7c3e5d1a8b6c2f4e9d0a1b3c7e5f8a6d2c4'
ALGORITHM='HS256'

bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

templates=Jinja2Templates(directory="TODO/templates")

@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html",{'request':request})

@router.get("/register-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("register.html",{'request':request})

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int,role:str,expire_delta:timedelta):
    encode={'sub':username,'id':user_id,'role':role}
    expires=datetime.now(timezone.utc)+expire_delta
    encode.update({'exp':expires})

    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get('sub')
        user_id:int=payload.get('id')
        user_role:str=payload.get('role')
        if username is None or user_id is None:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user')
        return {'username':username,'id':user_id,'user_role':user_role}
    except JWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user')




class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str

class Token(BaseModel):
    access_token:str
    token_type:str


@router.post('/',status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,create_user_request:CreateUserRequest):
    create_user_model=Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )

    db.add(create_user_model)

    db.commit()

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user') 
    
    token=create_access_token(user.username,user.id,user.role,timedelta(minutes=20))
    

    return {'access_token':token,'token_type':'bearer'}


    
