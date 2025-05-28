from fastapi import FastAPI
from .database import Base, engine
from .routes import users, personas, cobros, pdf, web_persona, web_cuenta, web_auth
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(users.router)
app.include_router(personas.router)
app.include_router(cobros.router)
app.include_router(pdf.router)
app.include_router(web_persona.router)
app.include_router(web_cuenta.router)
app.include_router(web_auth.router)