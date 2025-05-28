import os
import psycopg2
from jinja2 import Environment, FileSystemLoader
import subprocess
from datetime import datetime
from dateutil.relativedelta import relativedelta

class GestorCuentasCobro:
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
        
        # Conexión a la base de datos
        self.conn = psycopg2.connect(
            dbname="CuentasCobro",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()
    
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
        print("    SISTEMA DE CUENTAS DE COBRO")
        print("="*50)
        print("1. Gestionar Usuarios")
        print("2. Generar Cuenta de Cobro (PDF)")
        print("3. Salir")
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
        self.cursor.execute("""
            SELECT DISTINCT nombre_mio, cedula, lugar_cedula 
            FROM cuentas_cobro 
            ORDER BY nombre_mio
        """)
        usuarios = self.cursor.fetchall()
        
        if not usuarios:
            print("\nNo hay usuarios registrados.")
            return []
        
        print("\nUsuarios registrados:")
        for i, (nombre, cedula, lugar) in enumerate(usuarios):
            print(f"{i + 1}. {nombre} - C.C. {cedula} ({lugar})")
        
        return usuarios
    
    def crear_usuario_nuevo(self):
        """Crea un nuevo usuario con todos sus datos"""
        print("\n--- CREAR NUEVO USUARIO ---")
        
        # Datos del usuario
        nombre_mio = input("Nombre del emisor: ")
        cedula = input("Cédula: ")
        lugar_cedula = input("Lugar de expedición de la cédula: ")
        nombre_cuenta = input("Nombre del banco: ")
        numero_cuenta = input("Número de cuenta: ")
        fecha_input = input("Fecha (día/mes/año, ej: 1/06/2025): ")
        valor_numerico = input("Valor pagado numérico (sin puntos ni comas): ")
        valor_texto = input("Valor en texto (ej: un millón quinientos mil pesos): ")
        fecha_iso, periodo = self.formatear_periodo(fecha_input)
        numero_cuenta_doc = "1"
        
        self.insertar_cuenta_cobro({
            "numero_cuenta_doc": numero_cuenta_doc,
            "lugar_cedula": lugar_cedula,
            "fecha": fecha_iso,
            "nombre_mio": nombre_mio,
            "cedula": cedula,
            "valor_numerico": valor_numerico,
            "valor_texto": valor_texto,
            "periodo": periodo,
            "nombre_cuenta": nombre_cuenta,
            "numero_cuenta": numero_cuenta,
        })
        
        print("✅ Usuario y cuenta de cobro creados correctamente.")
    
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
        
        # Obtener datos bancarios existentes
        self.cursor.execute("""
            SELECT DISTINCT nombre_cuenta, numero_cuenta 
            FROM cuentas_cobro 
            WHERE nombre_mio = %s 
            LIMIT 1
        """, (nombre_mio,))
        
        datos_bancarios = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT MAX(CAST(numero_cuenta_doc AS INTEGER))
            FROM cuentas_cobro 
            WHERE nombre_mio ILIKE %s 
            AND numero_cuenta_doc::text ~ '^[0-9]+$'
        """, (nombre_mio,))
        
        # self.cursor.execute("""
        #     SELECT MAX(numero_cuenta_doc)
        #     FROM cuentas_cobro 
        #     WHERE nombre_mio ILIKE %s 
        #     AND numero_cuenta_doc IS NOT NULL
        # """, (nombre_mio,))

        ultimo_numero = self.cursor.fetchone()[0]
        siguiente_numero = (ultimo_numero + 1) if ultimo_numero else 1

        numero_cuenta_doc = str(siguiente_numero)
        nombre_cuenta, numero_cuenta = datos_bancarios if datos_bancarios else ("", "")
        
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
        
        # Procesar fecha y periodo
        fecha_iso, periodo = self.formatear_periodo(fecha_input)
        
        # Insertar nueva cuenta
        self.insertar_cuenta_cobro({
            "numero_cuenta_doc": numero_cuenta_doc,
            "lugar_cedula": lugar_cedula,
            "fecha": fecha_iso,
            "nombre_mio": nombre_mio,
            "cedula": cedula,
            "valor_numerico": valor_numerico,
            "valor_texto": valor_texto,
            "periodo": periodo,
            "nombre_cuenta": nombre_cuenta,
            "numero_cuenta": numero_cuenta,
        })
        
        print("✅ Cuenta de cobro adicional creada correctamente.")
    
    def editar_cuenta_existente(self):
        """Permite editar una cuenta de cobro existente"""
        print("\n--- EDITAR CUENTA EXISTENTE ---")
        
        usuario = self.seleccionar_usuario()
        if not usuario:
            return
        
        nombre_mio = usuario[0]
        
        # Mostrar cuentas del usuario
        self.cursor.execute("""
            SELECT id, numero_cuenta_doc, fecha, valor_numerico
            FROM cuentas_cobro
            WHERE nombre_mio ILIKE %s
            ORDER BY fecha DESC
        """, (nombre_mio,))
        
        cuentas = self.cursor.fetchall()
        
        if not cuentas:
            print("No se encontraron cuentas para este usuario.")
            return
        
        print(f"\nCuentas de {nombre_mio}:")
        for i, (id_cuenta, num_doc, fecha, valor) in enumerate(cuentas):
            print(f"{i + 1}. ID #{id_cuenta} | N° {num_doc} | Fecha: {fecha} | Valor: ${valor:,}")
        
        try:
            seleccion = int(input("\nSeleccione una cuenta para editar: ")) - 1
            id_cuenta = cuentas[seleccion][0]
        except (ValueError, IndexError):
            print("Selección inválida.")
            return
        
        # Obtener datos actuales
        self.cursor.execute("SELECT * FROM cuentas_cobro WHERE id = %s", (id_cuenta,))
        datos_actuales = self.cursor.fetchone()
        columnas = [desc[0] for desc in self.cursor.description]
        datos_dict = dict(zip(columnas, datos_actuales))
        
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
            valor_actual = datos_dict.get(campo, "")
            print(f"{i + 1}. {descripcion}: {valor_actual}")
        print(f"{len(campos_editables) + 1}. Cambiar fecha (actual: {datos_dict.get('fecha', '')})")
        print(f"{len(campos_editables) + 2}. Finalizar edición")
        
        while True:
            try:
                opcion = int(input("\nSeleccione campo a editar: "))
                
                if opcion == len(campos_editables) + 2:  # Finalizar
                    break
                elif opcion == len(campos_editables) + 1:  # Cambiar fecha
                    nueva_fecha = input("Nueva fecha (día/mes/año): ")
                    fecha_iso, nuevo_periodo = self.formatear_periodo(nueva_fecha)
                    datos_dict["fecha"] = fecha_iso
                    datos_dict["periodo"] = nuevo_periodo
                    print("✅ Fecha y periodo actualizados.")
                elif 1 <= opcion <= len(campos_editables):
                    campo = list(campos_editables.keys())[opcion - 1]
                    descripcion = campos_editables[campo]
                    valor_actual = datos_dict.get(campo, "")
                    nuevo_valor = input(f"Nuevo {descripcion} (actual: {valor_actual}): ")
                    if nuevo_valor.strip():
                        datos_dict[campo] = nuevo_valor
                        print(f"✅ {descripcion} actualizado.")
                else:
                    print("Opción inválida.")
                    
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        # Actualizar en la base de datos
        self.actualizar_cuenta_cobro(id_cuenta, datos_dict)
        print("✅ Cuenta de cobro actualizada correctamente.")
    
    def insertar_cuenta_cobro(self, datos):
        """Inserta una nueva cuenta de cobro"""
        query = """
        INSERT INTO cuentas_cobro (
            numero_cuenta_doc, lugar_cedula, fecha,
            nombre_mio, cedula, valor_numerico,
            valor_texto, periodo, nombre_cuenta, numero_cuenta
        ) VALUES (
            %(numero_cuenta_doc)s, %(lugar_cedula)s, %(fecha)s,
            %(nombre_mio)s, %(cedula)s, %(valor_numerico)s,
            %(valor_texto)s, %(periodo)s, %(nombre_cuenta)s, %(numero_cuenta)s
        )
        """
        self.cursor.execute(query, datos)
        self.conn.commit()
    
    def actualizar_cuenta_cobro(self, id_cuenta, datos):
        """Actualiza una cuenta de cobro existente"""
        campos = []
        valores = []
        
        for campo, valor in datos.items():
            if campo != 'id':
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        valores.append(id_cuenta)
        
        query = f"UPDATE cuentas_cobro SET {', '.join(campos)} WHERE id = %s"
        self.cursor.execute(query, valores)
        self.conn.commit()
    
    def generar_pdf(self):
        """Genera el PDF de una cuenta de cobro"""
        print("\n--- GENERAR CUENTA DE COBRO (PDF) ---")
        
        # Buscar por nombre
        nombre = input("Ingrese el nombre del destinatario de la cuenta de cobro: ")
        
        # Buscar cuentas
        self.cursor.execute("""
            SELECT id, numero_cuenta_doc, fecha, valor_numerico
            FROM cuentas_cobro
            WHERE nombre_mio ILIKE %s
            ORDER BY fecha DESC
        """, (nombre,))
        
        registros = self.cursor.fetchall()
        
        if not registros:
            print("No se encontraron cuentas de cobro para esa persona.")
            return
        
        # Mostrar listado de cuentas
        print("\nCuentas disponibles:")
        for i, (id, num_doc, fecha, valor) in enumerate(registros):
            print(f"{i + 1}. N° {num_doc} | ID#: {id} | Fecha: {fecha} | Valor: ${valor:,}")
        
        # Elegir una cuenta
        try:
            seleccion = int(input("\nSeleccione una cuenta por número: ")) - 1
            id_seleccionado = registros[seleccion][0]
        except (ValueError, IndexError):
            print("Selección inválida.")
            return
        
        # Obtener datos de la cuenta seleccionada
        self.cursor.execute("SELECT * FROM cuentas_cobro WHERE id = %s", (id_seleccionado,))
        row = self.cursor.fetchone()
        columnas = [desc[0] for desc in self.cursor.description]
        datos = dict(zip(columnas, row))
        
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
    
    def ejecutar(self):
        """Método principal que ejecuta el sistema"""
        print("🚀 Iniciando Sistema de Cuentas de Cobro...")
        
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
                        print("👋 ¡Hasta luego!")
                        break
                    else:
                        print("❌ Opción inválida. Por favor seleccione 1, 2 o 3.")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Saliendo del sistema...")
                    break
                    
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
        finally:
            self.cerrar_conexion()
    
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
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Función principal
def main():
    gestor = GestorCuentasCobro()
    gestor.ejecutar()

if __name__ == "__main__":
    main()