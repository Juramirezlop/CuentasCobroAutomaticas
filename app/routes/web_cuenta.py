from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import CuentaCobro, Persona, User
from app.auth import get_current_user
from app.generar_tex import generar_cuenta_tex, compilar_pdf_con_tectonic
from datetime import datetime
import shutil
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/cuenta")
def mostrar_formulario_cuenta(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    personas = db.query(Persona).filter(Persona.owner_id == current_user.id).all()
    return templates.TemplateResponse("cuenta_form.html", {"request": request, "personas": personas})

@router.post("/cuenta")
def crear_cuenta(
    request: Request,
    persona_id: int = Form(...),
    fecha: str = Form(...),
    valor_numerico: str = Form(...),
    valor_texto: str = Form(...),
    numero_cuenta: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    cuenta = CuentaCobro(
        persona_id=persona_id,
        fecha=fecha_dt,
        valor_numerico=valor_numerico,
        valor_texto=valor_texto,
        numero_cuenta=numero_cuenta,
        owner_id=current_user.id
    )
    db.add(cuenta)
    db.commit()

    tex_path = generar_cuenta_tex(cuenta.id)
    pdf_path = compilar_pdf_con_tectonic(tex_path)

    # Mover a /static/pdf con nombre basado en numero de cuenta
    destino = os.path.join("app/static/pdf", f"{cuenta.numero_cuenta}.pdf")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copy(pdf_path, destino)

    return RedirectResponse(url=f"/cuenta-generada/{cuenta.id}", status_code=303)

@router.get("/cuenta-generada/{cuenta_id}")
def cuenta_generada(cuenta_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cuenta = db.query(CuentaCobro).filter(CuentaCobro.id == cuenta_id, CuentaCobro.owner_id == current_user.id).first()
    if not cuenta:
        return RedirectResponse(url="/cuenta")
    return templates.TemplateResponse("cuenta_generada.html", {"request": request, "filename": f"{cuenta.numero_cuenta}.pdf"})

@router.get("/cuentas")
def ver_cuentas(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cuentas = db.query(CuentaCobro).filter(CuentaCobro.owner_id == current_user.id).order_by(CuentaCobro.fecha.desc()).all()
    return templates.TemplateResponse("cuenta_listado.html", {"request": request, "cuentas": cuentas})
