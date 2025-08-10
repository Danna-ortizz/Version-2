from pathlib import Path
import pyodbc

def ejecutar(query, descripcion):
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=agencia_viajes;Trusted_Connection=yes;'
        )
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(tuple(row))
        print(f"✅ {descripcion} ejecutada correctamente.")
        conn.close()
    except Exception as e:
        print(f"❌ Error al ejecutar: {e}")

# 1. PIVOT de reservas por mes y ciudad destino
ejecutar("""
    SELECT ciudad,
        ISNULL([1], 0) AS Ene, ISNULL([2], 0) AS Feb, ISNULL([3], 0) AS Mar,
        ISNULL([4], 0) AS Abr, ISNULL([5], 0) AS May, ISNULL([6], 0) AS Jun,
        ISNULL([7], 0) AS Jul, ISNULL([8], 0) AS Ago, ISNULL([9], 0) AS Sep,
        ISNULL([10], 0) AS Oct, ISNULL([11], 0) AS Nov, ISNULL([12], 0) AS Dic
    FROM (
        SELECT MONTH(r.fecha_reserva) AS mes, d.ciudad
        FROM core_reserva r
        JOIN paquetes_turisticos pt ON r.paquete_id = pt.id
        JOIN destino d ON pt.destino_id = d.id
    ) AS datos
    PIVOT (
        COUNT(mes) FOR mes IN ([1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12])
    ) AS pvt;
""", "PIVOT reservas por mes y destino")

# 2. Clasificación de clientes por frecuencia de reservas
ejecutar("""
    SELECT 
        c.nombre_completo,
        COUNT(r.id) AS total_reservas,
        CASE 
            WHEN COUNT(r.id) = 0 THEN 'Cliente Nuevo'
            WHEN COUNT(r.id) = 1 THEN 'Cliente Regular'
            ELSE 'Cliente Frecuente'
        END AS clasificacion
    FROM core_cliente c
    LEFT JOIN core_reserva r ON c.id = r.cliente_id
    GROUP BY c.nombre_completo;
""", "Clasificación de clientes por frecuencia")

# 3. Paquetes activos con reservas futuras
ejecutar("""
    SELECT pt.*
    FROM paquetes_turisticos pt
    WHERE pt.estado_paquete = 'Activo'
    AND EXISTS (
        SELECT 1 FROM core_reserva r
        WHERE r.paquete_id = pt.id AND r.fecha_reserva > GETDATE()
    );
""", "Paquetes activos con reservas futuras")

# 4. TOP 5 destinos más visitados
ejecutar("""
    SELECT TOP 5 
        d.ciudad,
        COUNT(r.id) AS total_reservas
    FROM core_reserva r
    JOIN paquetes_turisticos pt ON r.paquete_id = pt.id
    JOIN destino d ON pt.destino_id = d.id
    GROUP BY d.ciudad
    ORDER BY total_reservas DESC;
""", "Top 5 destinos más visitados")

