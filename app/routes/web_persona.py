from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Persona, User
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/persona")
def mostrar_formulario_persona(request: Request):
    return templates.TemplateResponse("persona_form.html", {"request": request})

@router.post("/persona")
def guardar_persona(
    request: Request,
    nombre_mio: str = Form(...),
    cedula: str = Form(...),
    lugar_cedula: str = Form(...),
    numero_cuenta: str = Form(...),
    nombre_persona: str = Form(...),
    nombre_cuenta: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    nueva = Persona(
        nombre_mio=nombre_mio,
        cedula=cedula,
        lugar_cedula=lugar_cedula,
        numero_cuenta=numero_cuenta,
        nombre_persona=nombre_persona,
        nombre_cuenta=nombre_cuenta,
        owner_id=current_user.id
    )
    db.add(nueva)
    db.commit()
    return RedirectResponse(url="/persona", status_code=303)
