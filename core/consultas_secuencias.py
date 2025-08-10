import pyodbc

def ejecutar(sql):
    try:
        with pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\\SQLEXPRESS;"
            "DATABASE=agencia_viajes;"
            "Trusted_Connection=yes;"
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            try:
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            except:
                pass
            conn.commit()
            print(" Consulta ejecutada correctamente.")
    except Exception as e:
        print(f" Error al ejecutar: {e}")

# Crear secuencias desde 1
ejecutar("DROP SEQUENCE IF EXISTS seq_cliente_id;")
ejecutar("CREATE SEQUENCE seq_cliente_id START WITH 1 INCREMENT BY 1;")

ejecutar("DROP SEQUENCE IF EXISTS seq_reserva_id;")
ejecutar("CREATE SEQUENCE seq_reserva_id START WITH 1 INCREMENT BY 1;")

ejecutar("DROP SEQUENCE IF EXISTS seq_paquete_id;")
ejecutar("CREATE SEQUENCE seq_paquete_id START WITH 1 INCREMENT BY 1;")

# Crear tabla de prueba para ver cómo se usan
ejecutar("DROP TABLE IF EXISTS Demo_Clientes_Secuencia;")
ejecutar("""
CREATE TABLE Demo_Clientes_Secuencia (
    id INT PRIMARY KEY,
    nombre NVARCHAR(100)
);
""")

# Insertar usando la secuencia
ejecutar("""
INSERT INTO Demo_Clientes_Secuencia (id, nombre)
VALUES (NEXT VALUE FOR seq_cliente_id, 'Cliente Prueba 1');
""")

ejecutar("""
INSERT INTO Demo_Clientes_Secuencia (id, nombre)
VALUES (NEXT VALUE FOR seq_cliente_id, 'Cliente Prueba 2');
""")

# Consultar los datos
ejecutar("SELECT * FROM Demo_Clientes_Secuencia;")
