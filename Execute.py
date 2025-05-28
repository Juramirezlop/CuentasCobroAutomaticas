import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import subprocess
from datetime import datetime
from dateutil.relativedelta import relativedelta

class GestorCuentasCobroExcel:
    def __init__(self):
        # Configurar Jinja2 con delimitadores personalizados
        self.env = Environment(
            loader=FileSystemLoader('.'),
            block_start_string='((*',
            block_end_string='*))',
            variable_start_string='(((',
            variable_end_string=')))',
            comment_start_string='((=',
            comment_end_string='=))',
        )
        
        # Archivo Excel donde se guardarán los datos
        self.archivo_excel = "cuentas_cobro.xlsx"
        
        # Inicializar archivo si no existe
        self.inicializar_archivo()
    
    def inicializar_archivo(self):
        """Crea el archivo Excel con la estructura si no existe"""
        if not os.path.exists(self.archivo_excel):
            # Estructura de columnas
            columnas = [
                'id', 'numero_cuenta_doc', 'lugar_cedula', 'fecha', 
                'nombre_mio', 'cedula', 'valor_numerico', 'valor_texto', 
                'periodo', 'nombre_cuenta', 'numero_cuenta'
            ]
            
            # Crear DataFrame vacío con las columnas
            df = pd.DataFrame(columns=columnas)
            df.to_excel(self.archivo_excel, index=False)
            print(f"✅ Archivo {self.archivo_excel} creado con la estructura inicial.")
    
    def leer_datos(self):
        """Lee todos los datos del archivo Excel"""
        try:
            df = pd.read_excel(self.archivo_excel)
            # Asegurar que la columna 'id' sea numérica
            if 'id' in df.columns and not df.empty:
                df['id'] = pd.to_numeric(df['id'], errors='coerce')
            return df
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return pd.DataFrame()
    
    def guardar_datos(self, df):
        """Guarda el DataFrame en el archivo Excel"""
        try:
            df.to_excel(self.archivo_excel, index=False)
            return True
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return False
    
    def obtener_siguiente_id(self, df):
        """Obtiene el siguiente ID disponible"""
        if df.empty or 'id' not in df.columns:
            return 1
        return int(df['id'].max()) + 1 if not df['id'].isna().all() else 1
    
    def formatear_periodo(self, fecha_input):
        """Formatea el periodo restando un mes a la fecha ingresada"""
        meses = {
            1:"enero", 2:"febrero", 3:"marzo", 4:"abril", 5:"mayo", 6:"junio",
            7:"julio", 8:"agosto", 9:"septiembre", 10:"octubre", 11:"noviembre", 12:"diciembre"
        }
        fecha_dt = datetime.strptime(fecha_input, "%d/%m/%Y")
        fecha_inicio = fecha_dt - relativedelta(months=1)
        texto = (
            f"{fecha_inicio.day} del mes de {meses[fecha_inicio.month]} del año {fecha_inicio.year} "
            f"hasta el día {fecha_dt.day} del mes de {meses[fecha_dt.month]} del año {fecha_dt.year}"
        )
        return fecha_dt.strftime("%Y-%m-%d"), texto
    
    def limpiar_nombre(self, texto):
        """Limpia el nombre para usar en archivos"""
        return texto.strip().replace(" ", "_").replace("ñ", "n").replace("Ñ", "N")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal"""
        print("\n" + "="*50)
        print("    SISTEMA DE CUENTAS DE COBRO (EXCEL)")
        print("="*50)
        print("1. Gestionar Usuarios")
        print("2. Generar Cuenta de Cobro (PDF)")
        print("3. Ver archivo Excel")
        print("4. Salir")
        print("-"*50)
    
    def mostrar_menu_usuarios(self):
        """Muestra el menú de gestión de usuarios"""
        print("\n" + "="*40)
        print("    GESTIÓN DE USUARIOS")
        print("="*40)
        print("1. Crear nuevo usuario")
        print("2. Crear cuenta adicional para usuario existente")
        print("3. Editar información de cuenta existente")
        print("4. Ver todos los usuarios")
        print("5. Volver al menú principal")
        print("-"*40)
    
    def listar_usuarios(self):
        """Lista todos los usuarios únicos"""
        df = self.leer_datos()
        
        if df.empty:
            print("\nNo hay usuarios registrados.")
            return []
        
        # Obtener usuarios únicos
        usuarios_unicos = df[['nombre_mio', 'cedula', 'lugar_cedula']].drop_duplicates()
        usuarios_list = usuarios_unicos.values.tolist()
        
        if not usuarios_list:
            print("\nNo hay usuarios registrados.")
            return []
        
        print("\nUsuarios registrados:")
        for i, (nombre, cedula, lugar) in enumerate(usuarios_list):
            print(f"{i + 1}. {nombre} - C.C. {cedula} ({lugar})")
        
        return usuarios_list
    
    def crear_usuario_nuevo(self):
        """Crea un nuevo usuario con todos sus datos"""
        print("\n--- CREAR NUEVO USUARIO ---")
        
        # Datos del usuario
        nombre_mio = input("Nombre del emisor: ")
        cedula = input("Cédula: ")
        lugar_cedula = input("Lugar de expedición de la cédula: ")
        nombre_cuenta = input("Nombre del banco: ")
        numero_cuenta = input("Número de cuenta: ")
        fecha_input = input("Fecha (día/mes/año), ej: 1/06/2025: ")
        valor_numerico = input("Valor pagado numérico (sin puntos ni comas): ")
        valor_texto = input("Valor en texto (ej: un millón quinientos mil pesos): ")
        
        fecha_iso, periodo = self.formatear_periodo(fecha_input)
        numero_cuenta_doc = "1"
        
        # Leer datos actuales
        df = self.leer_datos()
        nuevo_id = self.obtener_siguiente_id(df)
        
        # Crear nueva fila
        nueva_fila = {
            'id': nuevo_id,
            'numero_cuenta_doc': numero_cuenta_doc,
            'lugar_cedula': lugar_cedula,
            'fecha': fecha_iso,
            'nombre_mio': nombre_mio,
            'cedula': cedula,
            'valor_numerico': int(valor_numerico),
            'valor_texto': valor_texto,
            'periodo': periodo,
            'nombre_cuenta': nombre_cuenta,
            'numero_cuenta': numero_cuenta
        }
        
        # Agregar al DataFrame
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        
        if self.guardar_datos(df):
            print("✅ Usuario y cuenta de cobro creados correctamente.")
        else:
            print("❌ Error al guardar los datos.")
    
    def seleccionar_usuario(self):
        """Permite seleccionar un usuario existente"""
        usuarios = self.listar_usuarios()
        if not usuarios:
            return None
        
        try:
            seleccion = int(input("\nSeleccione un usuario por número: ")) - 1
            if 0 <= seleccion < len(usuarios):
                return usuarios[seleccion]
            else:
                print("Selección inválida.")
                return None
        except ValueError:
            print("Por favor ingrese un número válido.")
            return None
    
    def crear_cuenta_adicional(self):
        """Crea una cuenta adicional para un usuario existente"""
        print("\n--- CREAR CUENTA ADICIONAL ---")
        
        usuario = self.seleccionar_usuario()
        if not usuario:
            return
        
        nombre_mio, cedula, lugar_cedula = usuario
        df = self.leer_datos()
        
        # Obtener datos bancarios existentes del usuario
        usuario_data = df[df['nombre_mio'] == nombre_mio]
        if not usuario_data.empty:
            datos_bancarios = usuario_data.iloc[0]
            nombre_cuenta = datos_bancarios['nombre_cuenta']
            numero_cuenta = datos_bancarios['numero_cuenta']
        else:
            nombre_cuenta, numero_cuenta = "", ""
        
        # Obtener el siguiente número de cuenta para este usuario
        user_docs = df[df['nombre_mio'] == nombre_mio]['numero_cuenta_doc'].astype(str)
        numeric_docs = pd.to_numeric(user_docs, errors='coerce').dropna()
        siguiente_numero = int(numeric_docs.max()) + 1 if not numeric_docs.empty else 1
        numero_cuenta_doc = str(siguiente_numero)
        
        print(f"\nUsuario seleccionado: {nombre_mio}")
        print(f"Datos bancarios actuales: {nombre_cuenta} - {numero_cuenta}")
        
        cambiar_banco = input("¿Desea cambiar los datos bancarios? (s/n): ").lower() == 's'
        
        if cambiar_banco:
            nombre_cuenta = input("Nuevo nombre del banco: ")
            numero_cuenta = input("Nuevo número de cuenta: ")
        
        # Datos de la nueva cuenta de cobro
        fecha_input = input("Fecha (día/mes/año), ej: 1/06/2025: ")
        valor_numerico = input("Valor pagado numérico (sin puntos ni comas): ")
        valor_texto = input("Valor en texto (ej: un millón quinientos mil pesos): ")
        fecha_iso, periodo = self.formatear_periodo(fecha_input)
        nuevo_id = self.obtener_siguiente_id(df)
        
        # Crear nueva fila
        nueva_fila = {
            'id': nuevo_id,
            'numero_cuenta_doc': numero_cuenta_doc,
            'lugar_cedula': lugar_cedula,
            'fecha': fecha_iso,
            'nombre_mio': nombre_mio,
            'cedula': cedula,
            'valor_numerico': int(valor_numerico),
            'valor_texto': valor_texto,
            'periodo': periodo,
            'nombre_cuenta': nombre_cuenta,
            'numero_cuenta': numero_cuenta
        }
        
        # Agregar al DataFrame
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        
        if self.guardar_datos(df):
            print("✅ Cuenta de cobro adicional creada correctamente.")
        else:
            print("❌ Error al guardar los datos.")
    
    def editar_cuenta_existente(self):
        """Permite editar una cuenta de cobro existente"""
        print("\n--- EDITAR CUENTA EXISTENTE ---")
        
        usuario = self.seleccionar_usuario()
        if not usuario:
            return
        
        nombre_mio = usuario[0]
        df = self.leer_datos()
        
        # Filtrar cuentas del usuario
        cuentas_usuario = df[df['nombre_mio'] == nombre_mio].sort_values('fecha', ascending=False)
        
        if cuentas_usuario.empty:
            print("No se encontraron cuentas para este usuario.")
            return
        
        print(f"\nCuentas de {nombre_mio}:")
        for i, (_, row) in enumerate(cuentas_usuario.iterrows()):
            print(f"{i + 1}. ID #{row['id']} | N° {row['numero_cuenta_doc']} | Fecha: {row['fecha']} | Valor: ${row['valor_numerico']:,}")
        
        try:
            seleccion = int(input("\nSeleccione una cuenta para editar: ")) - 1
            cuenta_seleccionada = cuentas_usuario.iloc[seleccion]
            id_cuenta = cuenta_seleccionada['id']
        except (ValueError, IndexError):
            print("Selección inválida.")
            return
        
        # Campos editables
        campos_editables = {
            "numero_cuenta_doc": "Número de cuenta de cobro",
            "lugar_cedula": "Lugar de expedición de cédula",
            "valor_numerico": "Valor numérico",
            "valor_texto": "Valor en texto",
            "nombre_cuenta": "Nombre del banco",
            "numero_cuenta": "Número de cuenta"
        }
        
        print("\n¿Qué desea editar?")
        for i, (campo, descripcion) in enumerate(campos_editables.items()):
            valor_actual = cuenta_seleccionada[campo]
            print(f"{i + 1}. {descripcion}: {valor_actual}")
        print(f"{len(campos_editables) + 1}. Cambiar fecha (actual: {cuenta_seleccionada['fecha']})")
        print(f"{len(campos_editables) + 2}. Finalizar edición")
        
        cambios_realizados = False
        
        while True:
            try:
                opcion = int(input("\nSeleccione campo a editar: "))
                
                if opcion == len(campos_editables) + 2:  # Finalizar
                    break
                elif opcion == len(campos_editables) + 1:  # Cambiar fecha
                    nueva_fecha = input("Nueva fecha (día/mes/año): ")
                    fecha_iso, nuevo_periodo = self.formatear_periodo(nueva_fecha)
                    df.loc[df['id'] == id_cuenta, 'fecha'] = fecha_iso
                    df.loc[df['id'] == id_cuenta, 'periodo'] = nuevo_periodo
                    cambios_realizados = True
                    print("✅ Fecha y periodo actualizados.")
                elif 1 <= opcion <= len(campos_editables):
                    campo = list(campos_editables.keys())[opcion - 1]
                    descripcion = campos_editables[campo]
                    valor_actual = cuenta_seleccionada[campo]
                    nuevo_valor = input(f"Nuevo {descripcion} (actual: {valor_actual}): ")
                    if nuevo_valor.strip():
                        # Convertir a int si es valor_numerico
                        if campo == 'valor_numerico':
                            nuevo_valor = int(nuevo_valor)
                        df.loc[df['id'] == id_cuenta, campo] = nuevo_valor
                        cambios_realizados = True
                        print(f"✅ {descripcion} actualizado.")
                else:
                    print("Opción inválida.")
                    
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        # Guardar cambios si se realizaron
        if cambios_realizados:
            if self.guardar_datos(df):
                print("✅ Cuenta de cobro actualizada correctamente.")
            else:
                print("❌ Error al guardar los cambios.")
    
    def generar_pdf(self):
        """Genera el PDF de una cuenta de cobro"""
        print("\n--- GENERAR CUENTA DE COBRO (PDF) ---")
        
        # Buscar por nombre
        nombre = input("Ingrese el nombre del destinatario de la cuenta de cobro: ")
        df = self.leer_datos()
        
        # Buscar cuentas del usuario
        cuentas_usuario = df[df['nombre_mio'].str.contains(nombre, case=False, na=False)]
        cuentas_usuario = cuentas_usuario.sort_values('fecha', ascending=False)
        
        if cuentas_usuario.empty:
            print("No se encontraron cuentas de cobro para esa persona.")
            return
        
        # Mostrar listado de cuentas
        print("\nCuentas disponibles:")
        for i, (_, row) in enumerate(cuentas_usuario.iterrows()):
            print(f"{i + 1}. N° {row['numero_cuenta_doc']} | ID#: {row['id']} | Fecha: {row['fecha']} | Valor: ${row['valor_numerico']:,}")
        
        # Elegir una cuenta
        try:
            seleccion = int(input("\nSeleccione una cuenta por número: ")) - 1
            cuenta_seleccionada = cuentas_usuario.iloc[seleccion]
        except (ValueError, IndexError):
            print("Selección inválida.")
            return
        
        # Convertir a diccionario para el template
        datos = cuenta_seleccionada.to_dict()
        
        # Verificar que existe el template
        if not os.path.exists("cuenta_template.tex"):
            print("❌ Error: No se encontró el archivo cuenta_template.tex")
            return
        
        try:
            # Renderizar LaTeX
            template = self.env.get_template("cuenta_template.tex")
            rendered_tex = template.render(**datos)
            
            # Crear carpeta PDF si no existe
            os.makedirs("PDF", exist_ok=True)
            
            # Definir nombres de archivo
            nombre_archivo_base = f"cuenta_{self.limpiar_nombre(datos['nombre_mio'])}_{datos['numero_cuenta_doc']}"
            archivo_tex = f"{nombre_archivo_base}.tex"
            archivo_pdf = os.path.join("PDF", f"{nombre_archivo_base}.pdf")
            
            # Guardar archivo .tex temporal
            with open(archivo_tex, "w", encoding="utf-8") as f:
                f.write(rendered_tex)
            
            # Compilar usando Tectonic
            result = subprocess.run(["tectonic", "--outdir=PDF", archivo_tex], 
                                    capture_output=True, text=True)
            
            if result.returncode == 0:
                # Eliminar .tex temporal
                os.remove(archivo_tex)
                print(f"✅ PDF generado exitosamente: {archivo_pdf}")
            else:
                print(f"❌ Error al compilar PDF: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error al generar PDF: {str(e)}")
    
    def ver_archivo_excel(self):
        """Muestra información sobre el archivo Excel"""
        df = self.leer_datos()
        
        if df.empty:
            print("\n📊 El archivo Excel está vacío.")
            return
        
        print(f"\n📊 INFORMACIÓN DEL ARCHIVO: {self.archivo_excel}")
        print(f"📈 Total de registros: {len(df)}")
        print(f"👥 Usuarios únicos: {df['nombre_mio'].nunique()}")
        
        print("\n📋 Últimos 5 registros:")
        ultimos = df.tail(5)[['id', 'nombre_mio', 'numero_cuenta_doc', 'fecha', 'valor_numerico']]
        for _, row in ultimos.iterrows():
            print(f"  ID {row['id']}: {row['nombre_mio']} | N° {row['numero_cuenta_doc']} | {row['fecha']} | ${row['valor_numerico']:,}")
    
    def ejecutar(self):
        """Método principal que ejecuta el sistema"""
        print("🚀 Iniciando Sistema de Cuentas de Cobro (Excel)...")
        
        try:
            while True:
                self.mostrar_menu_principal()
                
                try:
                    opcion = input("Seleccione una opción: ").strip()
                    
                    if opcion == "1":
                        self.menu_usuarios()
                    elif opcion == "2":
                        self.generar_pdf()
                    elif opcion == "3":
                        self.ver_archivo_excel()
                    elif opcion == "4":
                        print("👋 ¡Hasta luego!")
                        break
                    else:
                        print("❌ Opción inválida. Por favor seleccione 1-4.")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Saliendo del sistema...")
                    break
                    
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
    
    def menu_usuarios(self):
        """Maneja el menú de gestión de usuarios"""
        while True:
            self.mostrar_menu_usuarios()
            
            try:
                opcion = input("Seleccione una opción: ").strip()
                
                if opcion == "1":
                    self.crear_usuario_nuevo()
                elif opcion == "2":
                    self.crear_cuenta_adicional()
                elif opcion == "3":
                    self.editar_cuenta_existente()
                elif opcion == "4":
                    self.listar_usuarios()
                elif opcion == "5":
                    break
                else:
                    print("❌ Opción inválida. Por favor seleccione 1-5.")
                    
            except KeyboardInterrupt:
                break

# Función principal
def main():
    gestor = GestorCuentasCobroExcel()
    gestor.ejecutar()

if __name__ == "__main__":
    main()