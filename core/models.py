
from django.db import models

class Cliente(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')  # Este campo 'id' es autoincrementable
    nombre_completo = models.TextField()
    email = models.EmailField()
    telefono = models.TextField()
    direccion = models.TextField()
    fecha_registro = models.DateField()
    tipo_documento = models.TextField(null = True, blank=True)  # Campo opcional
    numero_documento = models.TextField()

    def __str__(self):
        return self.nombre_completo  # Devuelve el nombre del cliente

class Destino(models.Model):
    ciudad = models.TextField()
    pais = models.TextField()
    descripcion = models.TextField()

    class Meta:
        db_table = 'destino'  # Especifica el nombre de la tabla en la base de datos

    def __str__(self):
        return f"{self.ciudad}, {self.pais}"

class PaqueteTuristico(models.Model):
    nombre_paquete = models.TextField()
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_dias = models.IntegerField()
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado_paquete = models.TextField()
    imagen = models.ImageField(upload_to='paquetes/', null=True, blank=True)
    cupos_disponibles = models.IntegerField(default=10)

    class Meta:
        db_table = 'paquetes_turisticos'  # Nombre de la tabla en la base de datos

    def __str__(self):
        return self.nombre_paquete

class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE)
    fecha_reserva = models.DateField(auto_now_add=True)
    estado_reserva = models.TextField()
    total_reserva = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.TextField()

class Alerta(models.Model):
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    fecha_alerta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alerta: {self.mensaje}"


class Reembolso(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reembolso {self.id} - ${self.monto}"


