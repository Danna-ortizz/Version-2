from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Destino, PaqueteTuristico, Cliente, Reserva

admin.site.register(Destino)
admin.site.register(PaqueteTuristico)
admin.site.register(Cliente)
admin.site.register(Reserva)