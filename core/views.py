from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db import connection
from .models import PaqueteTuristico, Cliente, Reserva
from .forms import ReservaForm
from collections import defaultdict

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

from .models import PaqueteTuristico, Cliente, Reserva, Alerta  # importar Alerta

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
                        (SELECT precio FROM paquetes_turisticos WHERE id = %s))
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

def log_usu(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'core/log_usu.html')


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




