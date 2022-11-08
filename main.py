from sys import prefix
from fastapi import FastAPI
from routers import service
from routers import login

app = FastAPI()
app.include_router(service.router, prefix='/services', tags=["Service"])
app.include_router(login.router, prefix='/auth', tags=["Auth"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
