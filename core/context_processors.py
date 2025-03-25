# context_processors.py
from .models import Notificacion

def notificaciones_context(request):
    if request.user.is_authenticated:
        # Obtener todas las notificaciones no leídas relacionadas con el usuario a través de tareas y sectores
        notificaciones_no_leidas = Notificacion.objects.filter(
            tarea__sector__in=request.user.sectores.all(),
            leida=False
        )
        return {
            'notificaciones_no_leidas': notificaciones_no_leidas,
            'cantidad_no_leidas': notificaciones_no_leidas.count(),
        }
    return {}