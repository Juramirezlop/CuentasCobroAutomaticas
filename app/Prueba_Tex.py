from app.generar_tex import generar_cuenta_tex, compilar_pdf_con_tectonic

tex_path = generar_cuenta_tex(cuenta_id=1)
print(f"LaTeX generado en: {tex_path}")

pdf_path = compilar_pdf_con_tectonic(tex_path)
print(f"✅ PDF generado en: {pdf_path}")
