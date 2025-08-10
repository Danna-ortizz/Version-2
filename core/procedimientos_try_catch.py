from pathlib import Path
import pyodbc

def ejecutar(nombre, sql):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\\SQLEXPRESS;"
            "DATABASE=agencia_viajes;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print(f"✅ Procedimiento '{nombre}' creado correctamente.")
    except Exception as e:
        print(f"❌ Error en '{nombre}':", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# 1. RegistrarReserva con TRY CATCH
ejecutar("sp_RegistrarReservaSeguro", '''
CREATE OR ALTER PROCEDURE sp_RegistrarReservaSeguro
    @cliente_id INT,
    @paquete_id INT,
    @fecha DATE,
    @metodo_pago VARCHAR(20)
AS
BEGIN
    BEGIN TRY
        INSERT INTO core_reserva (cliente_id, paquete_id, fecha_reserva, metodo_pago, estado_reserva)
        VALUES (@cliente_id, @paquete_id, @fecha, @metodo_pago, 'Activo');
        PRINT '✅ Reserva registrada correctamente.';
    END TRY
    BEGIN CATCH
        PRINT '❌ Error al registrar la reserva:';
        PRINT ERROR_MESSAGE();
    END CATCH
END;
''')

# 2. CancelarReserva con TRY CATCH y transacción
ejecutar("sp_CancelarReservaSeguro", '''
CREATE OR ALTER PROCEDURE sp_CancelarReservaSeguro
    @reserva_id INT
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;
        UPDATE core_reserva
        SET estado_reserva = 'Cancelado'
        WHERE id = @reserva_id;
        COMMIT TRANSACTION;
        PRINT '✅ Reserva cancelada exitosamente.';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT '❌ Error al cancelar la reserva:';
        PRINT ERROR_MESSAGE();
    END CATCH
END;
''')
