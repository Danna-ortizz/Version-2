from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Importar las vistas de autenticación

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(template_name='core/login.html'), name='login'), # Ruta de inicio de sesión
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Ruta de cierre de sesión

    # Rutas del cliente y administrador
    path('', views.inicio, name='inicio'),
    path('historial_reservas/<int:cliente_id>/', views.historial_reservas, name='historial_reservas'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('completar/<int:reserva_id>/', views.completar_reserva, name='completar_reserva'),
    path('reservar/', views.reservar_paquete, name='reservar'),  # esta es la que usa el formulario
    path('log_usu/', views.log_usu, name='log_usu'),
    # Rutas de administración
    path('alertas/', views.ver_alertas, name='ver_alertas'),
    path('reembolsos/', views.ver_reembolsos, name='ver_reembolsos'),
]
