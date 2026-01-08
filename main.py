from fastapi import FastAPI,Depends,HTTPException,Path,status,Request
from .models import Base
from .database import engine,SessionLocal
from .routers import auth,todos,admin,users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app=FastAPI()

Base.metadata.create_all(bind=engine)


app.mount("/static",StaticFiles(directory="TODO/static"),name="static")


@app.get('/')
def test(request:Request):
    return RedirectResponse(url='/todos/todo-page',status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

