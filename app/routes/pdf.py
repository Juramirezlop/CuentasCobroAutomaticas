from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.generar_tex import generar_cuenta_tex, compilar_pdf_con_tectonic

router = APIRouter()

@router.get("/cuenta-pdf/{cuenta_id}", response_class=FileResponse)
def obtener_cuenta_pdf(cuenta_id: int):
    try:
        tex_path = generar_cuenta_tex(cuenta_id)
        pdf_path = compilar_pdf_con_tectonic(tex_path)
        return FileResponse(path=pdf_path, filename=f"cuenta_cobro_{cuenta_id}.pdf", media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
