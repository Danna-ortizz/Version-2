from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'paquete', 'metodo_pago']


class log_usu(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)