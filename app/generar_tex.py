import os
import subprocess
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import CuentaCobro

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../latex_templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../output_tex")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generar_cuenta_tex(cuenta_id: int):
    db: Session = SessionLocal()
    cuenta = db.query(CuentaCobro).filter(CuentaCobro.id == cuenta_id).first()
    if not cuenta:
        raise ValueError("Cuenta no encontrada")

    persona = cuenta.persona
    nombre_mio = persona.nombre_mio.upper()
    nombre_persona = persona.nombre_persona.upper()
    nombre_cuenta= persona.nombre_cuenta.upper()
    fecha_actual = cuenta.fecha
    dia = fecha_actual.day
    mes_actual = fecha_actual.month
    año_actual = fecha_actual.year

    if mes_actual == 1:
        mes_anterior = 12
    else:
        mes_anterior = mes_actual - 1

    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    periodo_format = f"{dia} del mes de {meses[mes_anterior]} del año {año_actual} hasta el dia {dia} del {meses[mes_actual]} del año {año_actual}"

    # Renderizado LaTeX
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        block_start_string='((*',
        block_end_string='*))',
        variable_start_string='(((',
        variable_end_string=')))',
        comment_start_string='((=',
        comment_end_string='=))',
    )

    template = env.get_template("cuenta_template.tex")

    rendered_tex = template.render(
        nombre_mio=nombre_mio,
        cedula=persona.cedula,
        lugar_cedula=persona.lugar_cedula,
        numero_cuenta=persona.numero_cuenta,
        nombre_persona=nombre_persona,
        nombre_cuenta=nombre_cuenta,
        valor_numerico=cuenta.valor_numerico,
        valor_texto=cuenta.valor_texto,
        periodo=periodo_format,
        fecha=fecha_actual.strftime("%d/%m/%Y"),
        numero_cuenta_doc=cuenta.numero_cuenta
    )

    output_path = os.path.join(OUTPUT_DIR, f"cuenta_cobro_{cuenta.id}.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_tex)

    db.close()
    return output_path

def compilar_pdf_con_tectonic(tex_path: str):
    output_dir = os.path.join(os.path.dirname(__file__), "../output_pdf")
    os.makedirs(output_dir, exist_ok=True)

    tectonic_path = r"C:\Program Files\Tectonic\tectonic.exe"

    try:
        subprocess.run(
            [tectonic_path, tex_path, "--outdir", output_dir],check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Error al compilar PDF con Tectonic") from e

    pdf_filename = os.path.splitext(os.path.basename(tex_path))[0] + ".pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    return pdf_path
