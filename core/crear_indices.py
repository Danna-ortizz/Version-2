from pathlib import Path
import pyodbc

def ejecutar(consulta, descripcion):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\\SQLEXPRESS;"
            "DATABASE=agencia_viajes;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        cursor.execute(consulta)
        conn.commit()
        print(f" {descripcion} ejecutada correctamente.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f" Error al ejecutar {descripcion}: {e}")

# 1. Cambiar tipo de dato de tipo_documento para permitir índice
ejecutar("""
    ALTER TABLE core_cliente
    ALTER COLUMN tipo_documento NVARCHAR(50) NOT NULL;
""", "Cambio de tipo en tipo_documento")

# 2. Crear índice único compuesto en (numero_documento, tipo_documento)
ejecutar("""
    CREATE UNIQUE INDEX idx_documento_tipo
    ON core_cliente (numero_documento, tipo_documento);
""", "Índice único en (numero_documento, tipo_documento)")


