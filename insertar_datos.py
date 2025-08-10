import pyodbc
from datetime import date

# Conexión a la base de datos de SQL Server
conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"  # o el nombre real de tu instancia
    "DATABASE=agencia_viajes;"        # tu base de datos
    "Trusted_Connection=yes;"        # Usando autenticación de Windows
)

cursor = conexion.cursor()

# --- 1. Insertar destinos de ejemplo ---
destino = [
    ('Cancún', 'México', 'Playas del Caribe y sitios arqueológicos'),
    ('Ciudad de México', 'México', 'Capital cultural con museos y gastronomía'),
    ('París', 'Francia', 'Ciudad del amor, museos y arquitectura'),
    ('Cusco', 'Perú', 'Centro histórico y acceso a Machu Picchu'),
    ('Tokio', 'Japón', 'Tecnología, templos y cultura moderna'),
]

cursor.executemany(
    "INSERT INTO Destinos (ciudad, pais, descripcion) VALUES (?, ?, ?);",
    destino
)
conexion.commit()

# --- 2. Insertar paquetes turísticos ---
paquetes = [
    ('Aventura en Cancún', 'Incluye playas, snorkel y visitas arqueológicas', 12000.00, 5, 1, '2025-08-10', '2025-08-15', 'activo'),
    ('Tour Cultural CDMX', 'Museos, centro histórico y gastronomía', 8000.00, 4, 2, '2025-09-01', '2025-09-05', 'activo'),
    ('Viaje a París', 'Torre Eiffel, Louvre y crucero por el Sena', 25000.00, 7, 3, '2025-12-15', '2025-12-22', 'activo'),
    ('Exploración Perú', 'Machu Picchu y Valle Sagrado', 21000.00, 6, 4, '2025-11-01', '2025-11-07', 'activo'),
    ('Aventura en Japón', 'Tokio, Kioto y cultura japonesa', 30000.00, 10, 5, '2026-03-20', '2026-03-30', 'activo'),
    ('Relax en Bali', 'Playas, templos y spa', 27000.00, 8, 1, '2025-10-01', '2025-10-09', 'activo'),
    ('Ruta Maya', 'Chichen Itzá, Tulum y cenotes', 9000.00, 5, 2, '2025-07-25', '2025-07-30', 'finalizado'),
    ('Europa Express', 'París, Roma y Berlín en 12 días', 35000.00, 12, 3, '2025-09-10', '2025-09-22', 'activo'),
    ('Andes Trek', 'Excursiones por los Andes y cultura local', 18000.00, 6, 4, '2025-08-01', '2025-08-07', 'cancelado'),
    ('Primavera en Japón', 'Cerezos en flor, templos y festivales', 32000.00, 9, 5, '2026-04-01', '2026-04-10', 'activo'),
]

cursor.executemany(
    """INSERT INTO Paquetes_Turisticos 
    (nombre_paquete, descripcion, precio, duracion_dias, destino_id, fecha_inicio, fecha_fin, estado_paquete)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
    paquetes
)
conexion.commit()

print("¡Datos insertados correctamente!")
cursor.close()
conexion.close()
