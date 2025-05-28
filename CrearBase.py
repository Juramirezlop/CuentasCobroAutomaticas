import psycopg2

# Se tiene que crear la BD desde postgres con el nombre de CuentasCobro, luego se realiza la conexión
conn = psycopg2.connect(
    dbname="CuentasCobro",
    user="postgres", # Usuario en postgreSQL
    password="postgres", # Clave en postgreSQL
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

query = """
CREATE TABLE cuentas_cobro (
    id SERIAL PRIMARY KEY,
    numero_cuenta_doc INTEGER,
    lugar_cedula TEXT,
    fecha DATE,
    nombre_mio TEXT,
    cedula TEXT,
    valor_numerico BIGINT,
    valor_texto TEXT,
    periodo TEXT,
    nombre_cuenta TEXT,
    numero_cuenta TEXT
);
"""
cursor.execute(query)

conn.commit()
print("Tabla creada correctamente")

cursor.close()
conn.close()