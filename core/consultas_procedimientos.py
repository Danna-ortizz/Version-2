import pyodbc

# Configura la conexión
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=agencia_viajes;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Procedimientos almacenados
procedimientos = {
    "RegistrarReserva": """
    CREATE PROCEDURE RegistrarReserva
        @cliente_id INT,
        @paquete_id INT,
        @fecha DATE,
        @metodo_pago VARCHAR(20),
        @estado NVARCHAR(20)
    AS
    BEGIN
        SET NOCOUNT ON;
        INSERT INTO core_reserva (cliente_id, paquete_id, fecha_reserva, metodo_pago, estado_reserva)
        VALUES (@cliente_id, @paquete_id, @fecha, @metodo_pago, @estado);
    END;
    """,

    "HistorialCliente": """
    CREATE PROCEDURE HistorialCliente
        @cliente_id INT
    AS
    BEGIN
        SET NOCOUNT ON;
        SELECT R.id, R.fecha_reserva, P.nombre_paquete
        FROM core_reserva R
        JOIN paquetes_turisticos P ON R.paquete_id = P.id
        WHERE R.cliente_id = @cliente_id;
    END;
    """,

    "DestinosMasVendidos": """
    CREATE PROCEDURE DestinosMasVendidos
    AS
    BEGIN
        SET NOCOUNT ON;
        SELECT P.nombre_paquete, COUNT(*) AS total_reservas
        FROM core_reserva R
        JOIN paquetes_turisticos P ON R.paquete_id = P.id
        GROUP BY P.nombre_paquete
        ORDER BY total_reservas DESC;
    END;
    """,

    "GestionDisponibilidad": """
    CREATE PROCEDURE GestionDisponibilidad
        @paquete_id INT,
        @nuevo_estado NVARCHAR(20)
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE paquetes_turisticos
        SET estado_paquete = @nuevo_estado
        WHERE id = @paquete_id;
    END;
    """,

    "DescuentoTemporada": """
    CREATE PROCEDURE DescuentoTemporada
        @paquete_id INT,
        @porcentaje_descuento INT
    AS
    BEGIN
        SET NOCOUNT ON;
        -- Suponemos que `precio` no está, así que omitimos lógica
        PRINT '⚠️ No se pudo aplicar descuento porque la tabla no tiene columna precio.';
    END;
    """
}

# Crear procedimientos
for nombre, sql in procedimientos.items():
    try:
        cursor.execute(f"IF OBJECT_ID('{nombre}', 'P') IS NOT NULL DROP PROCEDURE {nombre}")
        cursor.execute(sql)
        print(f"✅ Procedimiento {nombre} creado correctamente.")
    except Exception as e:
        print(f"❌ Error al crear {nombre}: {e}")

conn.commit()

# Cadena de conexión
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=agencia_viajes;"
    "Trusted_Connection=yes;"
)

# Función común para ejecutar procedimientos almacenados
def ejecutar_proc(nombre_proc, parametros=()):
    try:
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                placeholders = ",".join(["?" for _ in parametros])
                cursor.execute(f"EXEC {nombre_proc} {placeholders}", parametros)
                try:
                    rows = cursor.fetchall()
                    for row in rows:
                        print(row)
                except:
                    pass
                print(f"✅ Procedimiento '{nombre_proc}' ejecutado correctamente.")
    except Exception as e:
        print(f"❌ Error al ejecutar '{nombre_proc}': {e}")



# 1. Registrar una reserva
ejecutar_proc("RegistrarReserva", (1, 2, '2025-07-31', 'Efectivo', 'Confirmada'))

# 2. Historial de viajes
ejecutar_proc("HistorialCliente", (1,))

# 3. Destinos más vendidos
ejecutar_proc("DestinosMasVendidos")

# 4. Cambiar estado del paquete
ejecutar_proc("GestionDisponibilidad", (2, 'Disponible'))

# 5. Intento de descuento (muestra advertencia)
ejecutar_proc("DescuentoTemporada", (2, 10))

cursor.close()
conn.close()
