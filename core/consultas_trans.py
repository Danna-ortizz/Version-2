from pathlib import Path
import pyodbc

def obtener_conexion():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=agencia_viajes;"
        "Trusted_Connection=yes;"
    )

def ejecutar_transaccion(sql: str, descripcion="Transacción"):
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            print(f"✅ {descripcion} ejecutada correctamente.")
    except Exception as e:
        print(f"❌ Error en {descripcion}:", e)

# PROCESO COMPLETO DE RESERVA + DETALLE
transaccion_reserva_completa = '''
BEGIN TRY
    BEGIN TRANSACTION;

    DECLARE @id_reserva INT;

    INSERT INTO core_reserva (cliente_id, paquete_id, fecha_reserva, estado_reserva, total_reserva, metodo_pago)
    VALUES (1, 2, GETDATE(), 'activa', 1200.00, 'Tarjeta');

    SET @id_reserva = SCOPE_IDENTITY();

    INSERT INTO detalle_reserva (reserva_id, tipo_servicio, proveedor, costo_unitario, cantidad, subtotal)
    VALUES (@id_reserva, 'Hospedaje', 'Hotel Buen Viaje', 400.00, 3, 1200.00);

    COMMIT;
END TRY
BEGIN CATCH
    ROLLBACK;
    PRINT '❌ Error en transacción de reserva: ' + ERROR_MESSAGE();
END CATCH;
'''
ejecutar_transaccion(transaccion_reserva_completa, "Reserva + Detalle")

# CANCELACIÓN DE RESERVA CON REEMBOLSO
transaccion_cancelacion = '''
BEGIN TRY
    BEGIN TRANSACTION;

    UPDATE core_reserva
    SET estado_reserva = 'cancelada'
    WHERE id = 1;

    INSERT INTO AuditoriaReservasModificadas (IdReserva, TotalAntes, TotalDespues, Usuario, FechaActualizacion)
    VALUES (1, 1200.00, 0.00, SYSTEM_USER, GETDATE());

    COMMIT;
END TRY
BEGIN CATCH
    ROLLBACK;
    PRINT '❌ Error al cancelar la reserva: ' + ERROR_MESSAGE();
END CATCH;
'''
ejecutar_transaccion(transaccion_cancelacion, "Cancelación con reembolso")

# EJEMPLO DE COMMIT / ROLLBACK EXPLÍCITO
ejemplo_commit_rollback = '''
BEGIN TRY
    BEGIN TRANSACTION;

    UPDATE core_reserva
    SET metodo_pago = 'Efectivo'
    WHERE id = 1;

    COMMIT;
END TRY
BEGIN CATCH
    ROLLBACK;
    PRINT '❌ Error en prueba COMMIT/ROLLBACK: ' + ERROR_MESSAGE();
END CATCH;
'''
ejecutar_transaccion(ejemplo_commit_rollback, "Prueba COMMIT / ROLLBACK")

# DEMOSTRACIÓN DE TRY / CATCH EN ERROR
transaccion_error_controlado = '''
BEGIN TRY
    BEGIN TRANSACTION;

    UPDATE core_reserva
    SET columna_inexistente = 'X'
    WHERE id = 1;

    COMMIT;
END TRY
BEGIN CATCH
    ROLLBACK;
    PRINT '✔️ TRY/CATCH funcionó: ' + ERROR_MESSAGE();
END CATCH;
'''
ejecutar_transaccion(transaccion_error_controlado, "Manejo de error TRY/CATCH")

