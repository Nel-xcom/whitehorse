from django.contrib import admin
from .models import PerfilPuesto

# Register your models here.

@admin.register(PerfilPuesto)
class PerfilPuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre_puesto', 'sector', 'responsable')
    search_fields = ('nombre_puesto', 'sector__nombre', 'responsable__username')