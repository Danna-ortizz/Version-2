# probar_conexion_sql.py
import os
import sys

def configurar_entorno_django():
    # Ajusta el nombre del módulo de settings si tu proyecto se llama distinto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agencia_viajes3.settings')
    try:
        import django
        django.setup()
    except Exception as error:
        print("❌ Error inicializando Django con tus settings:", error)
        sys.exit(1)

def probar_conexion_bd():
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            # Prueba 1: ping simple
            cursor.execute("SELECT 1 AS ping;")
            fila_ping = cursor.fetchone()

            # Prueba 2: datos de la conexión/servidor
            cursor.execute("""
                SELECT
                    DB_NAME()      AS base_datos,
                    @@SERVERNAME   AS servidor,
                    SUSER_SNAME()  AS usuario,
                    @@VERSION      AS version_sql
            """)
            fila_info = cursor.fetchone()

        print("✅ Conexión exitosa a SQL Server desde Django.")
        print("   Ping:", fila_ping[0])
        print("   Base de datos:", fila_info[0])
        print("   Servidor:", fila_info[1])
        print("   Usuario:", fila_info[2])
        print("   Versión SQL:", fila_info[3].splitlines()[0])  # solo la primera línea
        return 0
    except Exception as error:
        print("❌ No se pudo conectar a SQL Server desde Django.")
        print("   Detalle:", error)
        return 1

if __name__ == "__main__":
    configurar_entorno_django()
    codigo_salida = probar_conexion_bd()
    sys.exit(codigo_salida)
