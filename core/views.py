from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db import connection, transaction
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from collections import defaultdict
import logging

from .models import PaqueteTuristico, Cliente, Reserva, Alerta, Reembolso
from .forms import ReservaForm



def inicio(request):
    paquetes = PaqueteTuristico.objects.select_related('destino').all()
    form = ReservaForm()
    # Agrupar reservas por cliente
    reservas_por_cliente = defaultdict(list)
    reservas = Reserva.objects.select_related('cliente', 'paquete__destino').all()
    for r in reservas:
        reservas_por_cliente[r.cliente].append(r)

    return render(request, 'core/index.html', {
        'paquetes': paquetes,
        'form': form,
        'reservas_por_cliente': reservas_por_cliente.items()
    })



def reservar_paquete(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        tipo_doc = request.POST.get('tipo_documento')
        num_doc = request.POST.get('numero_documento')
        metodo_pago = request.POST.get('metodo_pago')
        paquete_id = request.POST.get('paquete_id')

        if not all([nombre, correo, tipo_doc, num_doc, metodo_pago, paquete_id]):
            messages.error(request, "Todos los campos obligatorios deben ser completados.")
            return redirect('inicio')

        try:
            with connection.cursor() as cursor:
                # Verificar que el paquete exista
                query = "SELECT COUNT(*) FROM paquetes_turisticos WHERE id = %s"
                params = [paquete_id]
                print(f"Ejecutando query: {query} con params: {params}")
                cursor.execute(query, params)
                result = cursor.fetchone()
                print(f"Resultado del cursor.fetchone(): {result}")

                if result[0] == 0:
                    messages.error(request, "El paquete turístico seleccionado no existe.")
                    return redirect('inicio')

                # Buscar cliente por tipo y número de documento
                query = """
                    SELECT id FROM core_cliente
                    WHERE tipo_documento = %s AND numero_documento = %s
                """
                params = [tipo_doc, num_doc]
                print(f"Ejecutando query: {query.strip()} con params: {params}")
                cursor.execute(query, params)
                cliente = cursor.fetchone()
                print(f"Resultado del cursor.fetchone(): {cliente}")

                if cliente:
                    cliente_id = cliente[0]
                    print(f"Cliente encontrado con id: {cliente_id}")
                    # Actualizar datos del cliente si ya existe (no está implementado aquí, solo print)
                    print(f"Aquí podrías actualizar los datos del cliente {cliente_id} si es necesario.")
                else:
                    # Insertar nuevo cliente
                    query = """
                        INSERT INTO core_cliente (
                            nombre_completo, email, telefono, direccion,
                            fecha_registro, tipo_documento, numero_documento
                        )
                        OUTPUT INSERTED.id
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    params = [
                        nombre, correo, telefono, direccion,
                        timezone.now().date(), tipo_doc, num_doc
                    ]
                    print(f"Ejecutando query: {query.strip()} con params: {params}")
                    cursor.execute(query, params)
                    cliente_id = cursor.fetchone()[0]
                    print(f"Nuevo cliente insertado con id: {cliente_id}")

                # Obtener el paquete y verificar los cupos
                paquete = PaqueteTuristico.objects.get(id=paquete_id)
                print(f"Paquete {paquete.nombre_paquete} tiene {paquete.cupos_disponibles} cupos disponibles")
                if paquete.cupos_disponibles <= 0:
                    messages.error(request, "Este paquete ya no tiene cupos disponibles.")
                    return redirect('inicio')

                # Descontar cupo y guardar el paquete
                paquete.cupos_disponibles -= 1
                paquete.save()
                print(f"Cupos descontados, ahora quedan {paquete.cupos_disponibles} cupos disponibles")

                # Insertar la reserva
                query = """
                    INSERT INTO core_reserva (
                        fecha_reserva, estado_reserva, metodo_pago,
                        cliente_id, paquete_id, total_reserva
                    )
                    VALUES (%s, %s, %s, %s, %s,
                        (SELECT precio FROM paquetes_turisticos WHERE id_pk = %s))
                """

                params = [
                    timezone.now().date(), 'pendiente', metodo_pago,
                    cliente_id, paquete_id, paquete_id
                ]
                print(f"Ejecutando query: {query.strip()} con params: {params}")
                cursor.execute(query, params)
                print(f"Reserva insertada correctamente")

                # Generar alerta si cupos son bajos
                if paquete.cupos_disponibles <= 2:
                    alerta = Alerta.objects.create(
                        paquete=paquete,
                        mensaje=f"Cupos bajos para el paquete {paquete.nombre_paquete}"
                    )
                    print(f"Alerta creada: {alerta.mensaje}")

                messages.success(request, "Reserva realizada correctamente.")

        except Exception as e:
            print(f"Excepción capturada: {e}")
            messages.error(request, f"Error al registrar la reserva: {e}")

        return redirect('inicio')

    paquetes = PaqueteTuristico.objects.all()
    return render(request, 'core/index.html', {'paquetes': paquetes})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import logging

logger = logging.getLogger(__name__)

def login_alt_view(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('form_rembolso')
            else:
                return render(request, 'core/login_alt.html', {
                    'error': 'Correo o contraseña incorrectos'
                })

        return render(request, 'core/login_alt.html')

    except Exception as e:
        logger.error(f"Error en login_alt_view: {e}")
        return render(request, 'core/login_alt.html', {
            'error': 'Ocurrió un error inesperado. Intenta nuevamente.'
        })


def login_view(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('form_rembolso')  # ← corregido: no uses 'core/form_rembolso'
            else:
                return render(request, 'core/login_alt.html', {
                    'error': 'Correo o contraseña incorrectos'
                })

        return render(request, 'core/login_alt.html')

    except Exception as e:
        logger.error(f"Error en login_view: {e}")
        return render(request, 'core/login_alt.html', {
            'error': 'Ocurrió un error inesperado. Intenta nuevamente.'
        })

from django.views.decorators.http import require_http_methods
from django.db import connection, transaction
from django.contrib import messages
from django.shortcuts import render, redirect


def form_rembolso(request):
    if request.method == "POST":
        # Acepta ambos nombres por si el HTML cambia
        idReserva = (
            (request.POST.get("reserva_id") or request.POST.get("order_id") or "").strip()
        )

        # Validaciones básicas
        if not idReserva:
            messages.error(request, "El ID de la reserva es obligatorio.")
            return redirect("form_rembolso")
        if not idReserva.isdigit():
            messages.error(request, "El ID de la reserva debe ser numérico.")
            return redirect("form_rembolso")

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # 1) Obtener total_reserva
                    cursor.execute("""
                        SELECT total_reserva
                        FROM core_reserva
                        WHERE id = %s
                    """, [idReserva])
                    fila = cursor.fetchone()
                    if not fila:
                        messages.error(request, "No existe una reserva con ese ID.")
                        return redirect("form_rembolso")
                    totalReserva = fila[0]

                    # 2) Evitar reembolso duplicado
                    cursor.execute("SELECT COUNT(*) FROM core_reembolso WHERE reserva_id = %s", [idReserva])
                    if cursor.fetchone()[0] > 0:
                        messages.warning(request, "Ya existe un reembolso para esta reserva.")
                        return redirect("form_rembolso")

                    # 3) Insertar reembolso (fecha = GETDATE())
                    cursor.execute("""
                        INSERT INTO core_reembolso (monto, fecha, reserva_id)
                        OUTPUT INSERTED.id
                        VALUES (%s, GETDATE(), %s)
                    """, [totalReserva, idReserva])
                    idNuevoReembolso = cursor.fetchone()[0]

            messages.success(
                request,
                f"Reembolso registrado (ID {idNuevoReembolso}) por ${float(totalReserva):.2f}."
            )
        except Exception as e:
            messages.error(request, f"Error al registrar el reembolso: {e}")
        return redirect("form_rembolso")

    # GET
    return render(request, "core/form_rembolso.html")


def estadisticos(request):
    # Aquí podrías agregar lógica para obtener estadísticas de reservas, destinos, etc.
    return render(request, 'core/estadisticos.html')

def historial_reservas(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    reservas = Reserva.objects.filter(cliente=cliente).select_related('paquete', 'paquete__destino')
    return render(request, 'core/historial_reservas.html', {
        'cliente': cliente,
        'reservas': reservas
    })


from .models import Reembolso

def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.estado_reserva != 'cancelada':
        reserva.estado_reserva = 'cancelada'
        reserva.save()

        # Crear reembolso automáticamente
        Reembolso.objects.create(
            reserva=reserva,
            monto=reserva.total_reserva
        )

        messages.success(request, "Reserva cancelada y reembolso registrado.")
    else:
        messages.error(request, "La reserva ya está cancelada.")

    return redirect('inicio')

# views.py
from django.shortcuts import render
from django.db import connection

def estadisticos(request):
    # --- Consulta 1: Top 5 Paquetes Más Reservados ---
    with connection.cursor() as cursor:
        cursor.execute("""
                       
            SELECT TOP (5)
                p.id AS paquete_id,
                p.nombre_paquete,
                COUNT(r.id) AS total_reservas,
                p.precio,
                p.destino_id,
                p.cupos_disponibles
            FROM paquetes_turisticos p
            LEFT JOIN core_reserva r ON p.id = r.paquete_id
            GROUP BY p.id, p.nombre_paquete, p.precio, p.destino_id, p.cupos_disponibles
            ORDER BY total_reservas DESC;
        """)
        rows = cursor.fetchall()

    paquetes = [
        {
            'id': row[0],
            'nombre': row[1],
            'reservas': row[2],
            'precio': row[3],
            'destino': row[4],
            'cupos': row[5]
        }
        for row in rows
    ]

    # --- Consulta 2: Pivot de Reservas por Mes y Paquete ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                FORMAT(CAST(r.fecha_reserva AS datetime), 'MMMM', 'es-MX') AS mes,
                p.nombre_paquete,
                COUNT(*) AS total
            FROM core_reserva r
            JOIN paquetes_turisticos p ON r.paquete_id = p.id
            GROUP BY FORMAT(CAST(r.fecha_reserva AS datetime), 'MMMM', 'es-MX'), p.nombre_paquete
            ORDER BY mes;
        """)
        pivot_rows = cursor.fetchall()

    # --- Procesar datos para tabla dinámica ---
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

    paquetes_pivot = sorted(list(set(row[1] for row in pivot_rows)))
    pivot_dict = defaultdict(dict)

    for mes in meses:
        pivot_dict[mes] = {paquete: 0 for paquete in paquetes_pivot}

    for mes, paquete, total in pivot_rows:
        mes = mes.lower()
        pivot_dict[mes][paquete] = total

    pivot_data = []
    for mes in meses:
        fila = {'mes': mes.title()}
        fila.update(pivot_dict[mes])
        pivot_data.append(fila)

    pivot_columns = ['mes'] + paquetes_pivot
# 🎨 Paleta de colores para el gráfico (tantos como paquetes_pivot)
    colores_chart = [
        f'hsl({(i * 40) % 360}, 70%, 50%)' for i in range(len(paquetes_pivot))
    ]

    # --- Renderizar template con ambos conjuntos ---
    return render(request, 'core/estadisticos.html', {
    'paquetes': paquetes,
    'pivot_data': pivot_data,
    'pivot_columns': pivot_columns,
    'colores_chart': colores_chart
})


def pagar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado_reserva = 'pagada'
    reserva.save()
    messages.success(request, "Reserva marcada como pagada.")
    return redirect('inicio')

def completar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reserva.estado_reserva = 'completada'
    reserva.save()
    messages.success(request, "Reserva marcada como completada.")
    return redirect('inicio')

from .models import Alerta, Reembolso

def ver_alertas(request):
    alertas = Alerta.objects.select_related('paquete').order_by('-fecha_alerta')
    return render(request, 'core/alertas.html', {
        'alertas': alertas
    })

from django.contrib.admin.views.decorators import staff_member_required
from.models import Reembolso
@staff_member_required
def ver_reembolsos(request):
    reembolsos = Reembolso.objects.select_related('reserva', 'reserva__cliente').order_by('-fecha')
    return render(request, 'core/reembolsos.html', {
        'reembolsos': reembolsos
    })

from django.shortcuts import redirect
from django.contrib.auth import views as auth_views  # Importar las vistas de autenticación

class CustomLoginView(auth_views.LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')  # Redirige al inicio si ya está logueado
        return super().get(request, *args, **kwargs)




