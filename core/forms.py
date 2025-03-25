from django import forms
from .models import Sector, Tarea,ProcesoEmpresarial, CustomUser, Notificacion, InstructivoGeneral, InstructivoCalidad, InstructivoTrabajo, FlujoTrabajo
from django.core.exceptions import ValidationError
from django.utils import timezone

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password', 'placeholder': 'Contraseña'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_confirm_password', 'placeholder': 'Confirmar Contraseña'})
    )

    class Meta:
        model = CustomUser  # Cambiamos User a CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de Usuario'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():  # Cambiamos User a CustomUser
            raise ValidationError("Este nombre de usuario ya está registrado. Intenta con otro.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():  # Cambiamos User a CustomUser
            raise ValidationError("Este correo electrónico ya está registrado. Utiliza uno diferente.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError({
                'confirm_password': "Las contraseñas no coinciden. Por favor, verifica e inténtalo de nuevo."
            })

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['nombre', 'descripcion']  # Esto debe ser una lista, no una tupla
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del Sector', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripción del Sector (Opcional)', 'class': 'form-control'}),
        }

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['nombre', 'descripcion', 'fecha_vencimiento', 'notificacion', 'prioridad', 'responsable']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notificacion': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
        }

class FlujoTrabajoForm(forms.ModelForm):
    class Meta:
        model = FlujoTrabajo
        fields = ['nombre', 'sector']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.Select(attrs={'class': 'form-control'}),
        }


class ProcesoEmpresarialForm(forms.ModelForm):
    class Meta:
        model = ProcesoEmpresarial
        fields = '__all__'

class InstructivoGeneralForm(forms.ModelForm):
    class Meta:
        model = InstructivoGeneral
        fields = ['nombre', 'descripcion_sector', 'logo_empresa'] 
        widgets = {
            'descripcion_sector': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del sector'}),
        }

class InstructivoTrabajoForm(forms.ModelForm):
    class Meta:
        model = InstructivoTrabajo
        fields = ['logo_empresa', 'nombre', 'codigo', 'version', 'objetivo', 'alcance', 'responsabilidades', 'pasos', 'equipo_requerido', 'medidas_seguridad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.NumberInput(attrs={'class': 'form-control'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsabilidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pasos': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'equipo_requerido': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medidas_seguridad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InstructivoCalidadForm(forms.ModelForm):
    class Meta:
        model = InstructivoCalidad
        fields = ['logo_empresa', 'nombre', 'codigo', 'version', 'objetivo', 'alcance', 'responsabilidades', 'pasos', 'criterios_evaluacion', 'normativa_asociada']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.NumberInput(attrs={'class': 'form-control'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'alcance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsabilidades': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pasos': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'criterios_evaluacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'normativa_asociada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class NotificacionForm(forms.ModelForm):
    class Meta:
        model = Notificacion
        fields = ['titulo', 'mensaje', 'dia', 'hora_envio', 'enviar_ahora']
        widgets = {
            'dia': forms.Select(attrs={'class': 'form-control'}),
            'hora_envio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.hora_envio:
            # Set a default time if none is provided
            self.fields['hora_envio'].initial = timezone.now().time()