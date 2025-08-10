from pathlib import Path
import pyodbc

def obtener_conexion():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=agencia_viajes;"
        "Trusted_Connection=yes;"
    )

def ejecutar(sql: str):
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            print("✅ Consulta ejecutada correctamente.")
    except Exception as e:
        print("❌ Error al ejecutar:", e)


# Tablas
ejecutar("DROP TABLE IF EXISTS AuditoriaIntentosReservaNoDisponibles;")
ejecutar("""
CREATE TABLE AuditoriaIntentosReservaNoDisponibles (
    IdCliente INT,
    IdPaquete INT,
    FechaIntento DATETIME DEFAULT GETDATE(),
    EstadoPaquete VARCHAR(50),
    Mensaje VARCHAR(255)
);
""")

ejecutar("DROP TABLE IF EXISTS AuditoriaReservasModificadas;")
ejecutar ("""
CREATE TABLE AuditoriaReservasModificadas (
    IdReserva INT,
    TotalAntes DECIMAL(10,2),
    TotalDespues DECIMAL(10,2),
    Usuario VARCHAR(100),
    FechaActualizacion DATETIME DEFAULT GETDATE()
);
""")

ejecutar("DROP TABLE IF EXISTS AuditoriaEstadoPaqueteAutomatico;")
ejecutar("""
CREATE TABLE AuditoriaEstadoPaqueteAutomatico (
    IdPaquete INT,
    EstadoAnterior VARCHAR(50),
    EstadoNuevo VARCHAR(50),
    FechaCambio DATETIME DEFAULT GETDATE()
);
""")

ejecutar("DROP TABLE IF EXISTS AuditoriaAlertasOcupacion;")
ejecutar("""
CREATE TABLE AuditoriaAlertasOcupacion (
    IdPaquete INT,
    CantidadReservas INT,
    Mensaje VARCHAR(255),
    FechaAlerta DATETIME DEFAULT GETDATE()
);
""")


# Triggers
ejecutar("DROP TRIGGER IF EXISTS trg_AuditoriaIntentoReserva;")
ejecutar("""
CREATE TRIGGER trg_AuditoriaIntentoReserva
ON core_reserva
AFTER INSERT
AS
BEGIN
    INSERT INTO AuditoriaIntentosReservaNoDisponibles (
        IdCliente, IdPaquete, EstadoPaquete, Mensaje
    )
    SELECT
        I.cliente_id,
        I.paquete_id,
        P.estado_paquete,
        'Se intentó reservar un paquete no disponible'
    FROM INSERTED I
    LEFT JOIN paquetes_turisticos P ON I.paquete_id = P.id
    WHERE P.estado_paquete <> 'activo';
END;
""")

ejecutar("DROP TRIGGER IF EXISTS trg_AuditoriaReservaModificada;")
ejecutar("""
CREATE TRIGGER trg_AuditoriaReservaModificada
ON core_reserva
AFTER UPDATE
AS
BEGIN
    INSERT INTO AuditoriaReservasModificadas (
        IdReserva, TotalAntes, TotalDespues, Usuario
    )
    SELECT
        D.id, D.total_reserva, I.total_reserva, SYSTEM_USER
    FROM INSERTED I
    JOIN DELETED D ON I.id = D.id
    WHERE D.total_reserva <> I.total_reserva;
END;
""")

ejecutar("DROP TRIGGER IF EXISTS trg_EstadoPaqueteFinalizado;")
ejecutar("""
CREATE TRIGGER trg_EstadoPaqueteFinalizado
ON paquetes_turisticos
AFTER UPDATE
AS
BEGIN
    INSERT INTO AuditoriaEstadoPaqueteAutomatico (
        IdPaquete, EstadoAnterior, EstadoNuevo
    )
    SELECT
        D.id,
        D.estado_paquete,
        I.estado_paquete
    FROM INSERTED I
    JOIN DELETED D ON I.id = D.id
    WHERE D.estado_paquete <> 'finalizado' AND I.estado_paquete = 'finalizado';
END;
""")

ejecutar("DROP TRIGGER IF EXISTS trg_AlertaBajaOcupacionAuditable;")
ejecutar("""
CREATE TRIGGER trg_AlertaBajaOcupacionAuditable
ON core_reserva
AFTER INSERT
AS
BEGIN
    DECLARE @paquete_id INT
    SELECT @paquete_id = paquete_id FROM inserted

    DECLARE @total INT
    SELECT @total = COUNT(*) FROM core_reserva WHERE paquete_id = @paquete_id

    INSERT INTO AuditoriaAlertasOcupacion (
        IdPaquete, CantidadReservas, Mensaje
    )
    VALUES (
        @paquete_id, @total, 'Paquete auditado por inserción.'
    )
END;
""")

# tablas de auditoria (• Registro automático de cambios en reservas y paquetes
#• Registro de usuario que realizó la modificación
#• Registro de Inserción, Eliminación
#)

# Auditoría: tabla de inserciones
ejecutar("DROP TABLE IF EXISTS AuditoriaReservasInsertadas;")
ejecutar("""
CREATE TABLE AuditoriaReservasInsertadas (
    IdReserva INT,
    FechaReserva DATE,
    UsuarioModificacion VARCHAR(100),
    FechaRegistro DATETIME DEFAULT GETDATE()
);
""")

# Trigger inserción
#• Registro de inserciones en la tabla core_reserva
ejecutar("DROP TRIGGER IF EXISTS trg_Auditoria_Reserva_Insert;")
ejecutar("""
CREATE TRIGGER trg_Auditoria_Reserva_Insert
ON core_reserva
AFTER INSERT
AS
BEGIN
    INSERT INTO AuditoriaReservasInsertadas (IdReserva, FechaReserva, UsuarioModificacion)
    SELECT id, fecha_reserva, SYSTEM_USER
    FROM inserted;
END;
""")

# Auditoría: tabla de eliminaciones
ejecutar("DROP TABLE IF EXISTS AuditoriaReservasEliminadas;")
ejecutar("""
CREATE TABLE AuditoriaReservasEliminadas (
    IdReserva INT,
    FechaReserva DATE,
    UsuarioModificacion VARCHAR(100),
    FechaEliminacion DATETIME DEFAULT GETDATE()
);
""")

# Trigger eliminación
#• Registro de eliminaciones en la tabla core_reserva
ejecutar("DROP TRIGGER IF EXISTS trg_Auditoria_Reserva_Delete;")
ejecutar("""
CREATE TRIGGER trg_Auditoria_Reserva_Delete
ON core_reserva
AFTER DELETE
AS
BEGIN
    INSERT INTO AuditoriaReservasEliminadas (IdReserva, FechaReserva, UsuarioModificacion)
    SELECT id, fecha_reserva, SYSTEM_USER
    FROM deleted;
END;
""")



