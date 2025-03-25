"""
-----------------GUIDE-----------------

COMING SOON...

"""



#--IMPORTS

from django.shortcuts import render, redirect, get_object_or_404
from django.db import models, transaction
from datetime import datetime, date, timedelta
from django.contrib import messages
from .forms import RegisterForm, SectorForm, TareaForm, ProcesoEmpresarialForm, NotificacionForm, UserUpdateForm, InstructivoTrabajoForm, InstructivoCalidadForm, InstructivoGeneralForm, FlujoTrabajoForm
from .models import Sector, Tarea, ProcesoEmpresarial, CustomUser, Notificacion, SolicitudTarea, Comentario, PerfilPuesto, InstructivoGeneral, InstructivoCalidad, InstructivoTrabajo, FlujoTarea, FlujoTrabajo
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from .tasks import enviar_notificaciones_programadas, enviar_notificacion_a_usuario, enviar_notificacion_tarea
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, F, ExpressionWrapper, DurationField, FloatField
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Value, CharField
from django.db.models.functions import Concat
from collections import Counter
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
import logging
from functools import wraps

#----
def loading_view(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.GET.get('loading') == 'true':
            return render(request, 'loading.html')
        return view_func(request, *args, **kwargs)
    return wrapper

@loading_view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Encriptar la contraseña
            user.save()
            auth_login(request, user)  # Autenticar al usuario inmediatamente después del registro
            return redirect('seleccionar_sector')  # Redirigir a seleccionar_sector
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

#----
@loading_view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.sector and ProcesoEmpresarial.objects.filter(sector=user.sector, aceptado_por=user).exists():
                return redirect('agregar_sector')  # Redirige directamente si ya firmó
            elif user.sector:
                return redirect('ver_proceso', sector_id=user.sector.id)
            else:
                return redirect('seleccionar_sector')
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Inténtalo de nuevo.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def render_header(request):
    usuario = request.user
    notificaciones_no_leidas = Notificacion.objects.filter(
        tarea__sector=usuario.sector, leida=False
    )
    return render(request, 'header_template.html', {
        'notificaciones': notificaciones_no_leidas,
        'cantidad_no_leidas': notificaciones_no_leidas.count()
    })

@loading_view
@login_required
def agregar_sector(request):
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            sector = form.save()  # Guardar el sector
            request.user.sectores.add(sector)  # Relacionar el sector con el usuario actual
            messages.success(request, "Sector agregado exitosamente.")
            return redirect('agregar_sector')
    else:
        form = SectorForm()
    
    # Obtener los sectores relacionados al usuario actual
    sectores = request.user.sectores.all()

    return render(request, 'agregar_sector.html', {'form': form, 'sectores': sectores})


@login_required
def borrar_sector(request, sector_id):
    if request.method == 'POST': 
        try:
            # Verificar si el sector pertenece a los sectores del usuario
            sector = get_object_or_404(Sector, id=sector_id)
            if request.user.sectores.filter(id=sector.id).exists():
                sector.delete()
                return JsonResponse({'status': 'success', 'message': 'Sector eliminado exitosamente.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para eliminar este sector.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al eliminar el sector: {str(e)}'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})



@csrf_exempt
@login_required
def actualizar_sectores(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sector_id = data.get('sector_id')
        action = data.get('action')

        sector = get_object_or_404(Sector, id=sector_id)

        if action == 'add':
            request.user.sectores.add(sector)
            message = f"Sector {sector.nombre} asignado."
        elif action == 'remove':
            request.user.sectores.remove(sector)
            message = f"Sector {sector.nombre} removido."
        else:
            return JsonResponse({'status': 'error', 'message': 'Acción no válida.'})

        return JsonResponse({'status': 'success', 'message': message, 'action': action})

@loading_view
@login_required
def gestion_tareas(request, sector_id):
    """
    Vista para gestionar las tareas de un sector.
    """
    sector = get_object_or_404(Sector, id=sector_id)

    # Validar que el sector corresponde al usuario actual
    if sector not in request.user.sectores.all():
        return HttpResponseForbidden("No tienes permiso para acceder a las tareas de este sector.")

    tareas = sector.tareas.all().order_by('estado', 'fecha_vencimiento')

    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.sector = sector  # Asignar el sector a la tarea
            tarea.estado = 'Pendiente'  # Estado por defecto
            tarea.save()
            messages.success(request, "Tarea agregada exitosamente.")
            return redirect('gestion_tareas', sector_id=sector_id)
    else:
        form = TareaForm()

    return render(request, 'gestion_tareas.html', {
        'sector': sector,
        'tareas': tareas,
        'form': form
    })


@login_required
def borrar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    sector_id = tarea.sector.id
    tarea.delete()
    messages.success(request, "Tarea eliminada exitosamente.")
    return redirect('gestion_tareas', sector_id=sector_id)

@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.method == 'POST' and 'nombre' in request.POST:
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            messages.success(request, "Los cambios en la tarea han sido guardados exitosamente.")
            return redirect('gestion_tareas', sector_id=tarea.sector.id)
        else:
            print(form.errors)  # Esto muestra cualquier error de validación en la consola
            messages.error(request, "Error al guardar los cambios. Revisa los campos.")
    else:
        form = TareaForm(instance=tarea)

    return render(request, 'editar_tareas.html', {
        'tarea': tarea,
        'form': form
    })

@loading_view
def gestionar_notificaciones(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    notificaciones_no_leidas = tarea.notificaciones.filter(leida=False)

    if request.method == 'POST':
        form = NotificacionForm(request.POST)
        if form.is_valid():
            notificacion = form.save(commit=False)
            notificacion.tarea = tarea
            notificacion.save()

            # Envía solo si enviar_ahora está marcado
            if notificacion.enviar_ahora:
                enviar_notificacion_a_usuario(notificacion)
                # Marcar la notificación como leída (enviada) solo si es inmediata
                notificacion.leida = True
                notificacion.save()
                messages.success(request, "Notificación enviada inmediatamente.")
            else:
                messages.success(request, "Notificación creada y programada.")

            form = NotificacionForm()  # Limpia el formulario después de la creación

    else:
        form = NotificacionForm()

    return render(request, 'editar_tareas.html', {
        'form': form,
        'tarea': tarea,
        'notificaciones': notificaciones_no_leidas,
        'cantidad_no_leidas': notificaciones_no_leidas.count()
    })



@require_POST
@login_required
def marcar_todas_como_leidas(request):
    usuario = request.user
    # Marcar todas las notificaciones del sector del usuario como leídas
    Notificacion.objects.filter(tarea__sector=usuario.sector, leida=False).update(leida=True)
    return JsonResponse({'status': 'success'})


@login_required
def actualizar_notificacion(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.method == 'POST' and 'notificacion' in request.POST:
        tarea.notificacion = request.POST['notificacion']
        tarea.save()
        messages.success(request, "La notificación de la tarea ha sido actualizada.")
        return redirect('editar_tarea', tarea_id=tarea.id)
    
@loading_view
@login_required
def crear_proceso(request, sector_id, tipo_proceso):
    """
    Crea un documento de bienvenida (Instructivo General) o un proceso empresarial (IT / IC).
    """
    sector = get_object_or_404(Sector, id=sector_id)

    # Determinar el tipo de formulario y modelo según el tipo de proceso
    if tipo_proceso == "instructivo_general":
        form_class = InstructivoGeneralForm
        instructivo_model = InstructivoGeneral

        # **🔹 Verificar si ya existe un instructivo general para este sector**
        instructivo_existente = instructivo_model.objects.filter(sector=sector).first()
        if instructivo_existente:
            messages.error(request, "Este sector ya tiene un instructivo general. Debes editar el existente.")
            return redirect("editar_proceso", sector_id=sector.id, tipo_proceso="instructivo_general", proceso_id=instructivo_existente.id)

    elif tipo_proceso == "IT":
        form_class = InstructivoTrabajoForm
        instructivo_model = InstructivoTrabajo
    elif tipo_proceso == "IC":
        form_class = InstructivoCalidadForm
        instructivo_model = InstructivoCalidad
    else:
        messages.error(request, "Tipo de instructivo inválido.")
        return redirect("procesos_digitales", sector_id=sector.id)

    # Lógica para manejar el formulario
    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            instructivo = form.save(commit=False)
            instructivo.sector = sector
            instructivo.creado_por = request.user  # Asignamos el usuario creador
            instructivo.save()
            messages.success(request, f"Instructivo {tipo_proceso} creado con éxito.")
            return redirect("procesos_digitales", sector_id=sector.id)
    else:
        form = form_class()

    return render(request, "crear_proceso.html", {
        "form": form,
        "sector": sector,
        "tipo_proceso": tipo_proceso
    })

@loading_view
@login_required
def procesos_digitales(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)

    # ✅ Obtener instructivos del sector
    instructivo_general = InstructivoGeneral.objects.filter(sector=sector).first()
    instructivos_trabajo = InstructivoTrabajo.objects.filter(sector=sector)
    instructivos_calidad = InstructivoCalidad.objects.filter(sector=sector)

    # ✅ Convertimos a JSON para cargar dinámicamente en el `select` del modal
    procesos_json = {
        "instructivo_general": [{"id": instructivo_general.id, "nombre": instructivo_general.nombre}] if instructivo_general else [],
        "IT": list(instructivos_trabajo.values("id", "nombre")),
        "IC": list(instructivos_calidad.values("id", "nombre"))
    }

    return render(request, 'procesos_digitales.html', {
        'sector': sector,
        'instructivo_general': instructivo_general,
        'instructivos_trabajo': instructivos_trabajo,
        'instructivos_calidad': instructivos_calidad,
        'procesos_json': procesos_json  # ✅ Pasamos los procesos al frontend
    })


@loading_view
@login_required
def editar_proceso(request, sector_id, tipo_proceso, proceso_id):
    """
    Vista para editar un proceso empresarial o instructivo.
    """
    if tipo_proceso == "instructivo_general":
        modelo = InstructivoGeneral
        form_class = InstructivoGeneralForm
    elif tipo_proceso == "IT":
        modelo = InstructivoTrabajo
        form_class = InstructivoTrabajoForm
    elif tipo_proceso == "IC":
        modelo = InstructivoCalidad
        form_class = InstructivoCalidadForm
    else:
        messages.error(request, "Tipo de proceso inválido.")
        return redirect("procesos_digitales", sector_id=sector_id)

    proceso = get_object_or_404(modelo, id=proceso_id, sector_id=sector_id)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=proceso)
        if form.is_valid():
            form.save()
            messages.success(request, f"{tipo_proceso} actualizado correctamente.")
            return redirect("procesos_digitales", sector_id=sector_id)
    else:
        form = form_class(instance=proceso)

    return render(request, "editar_proceso.html", {
        "form": form,
        "proceso": proceso,
        "tipo_proceso": tipo_proceso,
        "sector_id": sector_id
    })

@loading_view
@login_required
def eliminar_proceso(request, proceso_id):
    """
    Elimina cualquier tipo de proceso y redirige a la lista actualizada.
    """
    proceso = (
        InstructivoGeneral.objects.filter(id=proceso_id).first() or
        InstructivoTrabajo.objects.filter(id=proceso_id).first() or
        InstructivoCalidad.objects.filter(id=proceso_id).first()
    )

    if not proceso:
        messages.error(request, "El proceso no existe o ya fue eliminado.")
        return redirect(request.META.get('HTTP_REFERER', 'procesos_digitales'))

    # Verificar que el usuario pertenece al sector del proceso
    if not request.user.sectores.filter(id=proceso.sector.id).exists():
        messages.error(request, "No tienes permiso para eliminar este proceso.")
        return redirect(request.META.get('HTTP_REFERER', 'procesos_digitales'))

    proceso.delete()
    messages.success(request, "Proceso eliminado exitosamente.")

    return redirect(request.META.get('HTTP_REFERER', 'procesos_digitales'))

@login_required
def actualizar_logo(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    proceso = get_object_or_404(ProcesoEmpresarial, sector=sector)

    if request.method == 'POST':
        if 'nuevo_logo' in request.FILES:
            proceso.logo = request.FILES['nuevo_logo']
            proceso.save()
            messages.success(request, "El logo ha sido actualizado exitosamente.")
        else:
            messages.error(request, "Error al cargar el nuevo logo.")

    return redirect('crear_proceso_empresarial', sector_id=sector_id)

@login_required
def flujos_trabajo(request):
    """Renderiza la sección inicial de Flujos de Trabajo."""
    return render(request, 'flujos_trabajo.html')

@login_required
def obtener_tareas_por_sector(request):
    """ Devuelve las tareas de un sector específico en formato JSON """
    sector_id = request.GET.get('sector')
    if sector_id:
        tareas = Tarea.objects.filter(sector_id=sector_id).values('id', 'nombre')
        return JsonResponse(list(tareas), safe=False)
    return JsonResponse([], safe=False)

@login_required
def proceso_flujo_trabajo(request):
    """Vista para manejar los pasos del flujo."""
    sectores = Sector.objects.all()
    usuarios = CustomUser.objects.all()
    tareas = Tarea.objects.all()
    return render(request, 'flujos_trabajo.html', {
        'sectores': sectores,
        'usuarios': usuarios,
        'tareas': tareas
    })

@login_required
def api_tareas(request):
    """Devuelve las tareas de un sector con sus responsables en formato JSON."""
    sector_id = request.GET.get('sector')
    if sector_id:
        tareas = Tarea.objects.filter(sector_id=sector_id).values(
            'id', 'nombre', 'responsable__id', 'responsable__username'
        )
        return JsonResponse(list(tareas), safe=False)
    return JsonResponse([], safe=False)  # ✅ Devuelve array vacío si no hay sector



@login_required
def api_usuarios_por_tarea(request):
    """Devuelve los usuarios asignados a una tarea específica en formato JSON."""
    tarea_id = request.GET.get('tarea_id')
    if tarea_id:
        tarea = Tarea.objects.filter(id=tarea_id).first()
        if tarea and tarea.responsable:
            return JsonResponse([{'id': tarea.responsable.id, 'username': tarea.responsable.username}], safe=False)
    return JsonResponse([], safe=False)

@login_required
def guardar_orden_tareas(request):
    """Guarda el orden de las tareas del flujo"""
    if request.method == 'POST':
        data = json.loads(request.body)
        flujo_id = data.get('flujo_id')
        tareas_ordenadas = data.get('tareas_ordenadas')

        flujo = get_object_or_404(FlujoTrabajo, id=flujo_id)
        for tarea_ordenada in tareas_ordenadas:
            flujo_tarea = FlujoTarea.objects.get(flujo=flujo, tarea_id=tarea_ordenada['id'])
            flujo_tarea.orden = tarea_ordenada['orden']
            flujo_tarea.save()

        return JsonResponse({'success': True, 'message': 'Orden de tareas guardado exitosamente'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=400)

@login_required
def guardar_flujo_trabajo(request):
    """Guardar la información del flujo en la base de datos."""
    if request.method == 'POST':
        data = json.loads(request.body)
        nombre = data.get('nombre')
        sector_id = data.get('sector')
        tareas_data = data.get('tareas')

        flujo = FlujoTrabajo.objects.create(nombre=nombre, sector_id=sector_id)

        for tarea in tareas_data:
            try:
                tarea_id = int(tarea.get('tarea_id'))
                responsable_id = tarea.get('responsable_id')  # <- Cambiado, no se convierte en int si es None
                orden = int(tarea.get('orden'))

                FlujoTarea.objects.create(
                    flujo=flujo,
                    tarea_id=tarea_id,
                    responsable_id=int(responsable_id) if responsable_id and responsable_id != 'null' else None,  # ✅ Verificación extra
                    orden=orden
                )


            except ValueError as e:
                print(f"❌ Error al procesar la tarea: {e}")
                return JsonResponse({'success': False, 'message': str(e)}, status=400)

        return JsonResponse({'success': True, 'message': 'Flujo de trabajo creado exitosamente'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=400)



@login_required
def seleccionar_sector(request):
    if request.user.sectores.exists():
        # Si el usuario ya tiene sectores asignados, redirigir automáticamente a la firma de procesos
        return redirect('ver_procesos', sector_id=request.user.sectores.first().id)

    if request.method == 'POST':
        sector_ids = request.POST.getlist('sector_ids')
        sectores = Sector.objects.filter(id__in=sector_ids)

        # Asignar sectores seleccionados al usuario
        request.user.sectores.set(sectores)

        # Redirigir al primer instructivo general del primer sector seleccionado
        if sectores.exists():
            return redirect('ver_procesos', sector_id=sectores.first().id)
        else:
            messages.error(request, "Debes seleccionar al menos un sector.")
            return redirect('seleccionar_sector')

    sectores = Sector.objects.all()
    return render(request, 'seleccionar_sector.html', {'sectores': sectores})



logger = logging.getLogger(__name__)

@loading_view
@login_required
def ver_procesos(request, sector_id=None):
    """
    Vista para mostrar el Instructivo General del sector y manejar la firma digital del usuario.
    """

    # Obtener sector_id desde la URL o Query Params
    if sector_id is None:
        sector_id = request.GET.get("sector_id")

    if not sector_id:
        return HttpResponseBadRequest("Falta sector_id")

    sector = get_object_or_404(Sector, id=sector_id)
    instructivo = InstructivoGeneral.objects.filter(sector=sector).first()
    usuarios_sector = CustomUser.objects.filter(sectores=sector)
    perfiles_puesto = PerfilPuesto.objects.filter(sector=sector)

    # ✅ Definir la variable sectores_usuario al inicio
    sectores_usuario = request.user.sectores.all()

    # Obtener usuarios con sus perfiles
    usuarios_con_perfil = []
    for usuario in usuarios_sector:
        perfil = perfiles_puesto.filter(responsable=usuario).first()
        usuarios_con_perfil.append({
            'nombre': f"{usuario.first_name} {usuario.last_name}",
            'perfil': perfil.nombre_puesto if perfil else "Sin perfil de puesto definido",
            'descripcion': perfil.descripcion if perfil else ""
        })

    # ✅ Verificar si el usuario ya firmó este instructivo
    if instructivo and request.user in instructivo.firmado_por.all():
        # Buscar el siguiente instructivo sin firmar
        siguiente_instructivo = InstructivoGeneral.objects.filter(
            sector__in=sectores_usuario  # ✅ Ahora sectores_usuario está definido
        ).exclude(firmado_por=request.user).first()

        if siguiente_instructivo:
            return redirect("ver_procesos", sector_id=siguiente_instructivo.sector.id)
        else:
            return redirect("home")

    if request.method == "POST":
        if instructivo:
            instructivo.firmado_por.add(request.user)
            instructivo.save()

            # Buscar el siguiente instructivo sin firmar
            siguiente_instructivo = InstructivoGeneral.objects.filter(
                sector__in=sectores_usuario  # ✅ Ahora sectores_usuario está definido
            ).exclude(firmado_por=request.user).first()

            if siguiente_instructivo:
                return redirect("ver_procesos", sector_id=siguiente_instructivo.sector.id)
            else:
                return redirect("home")

    return render(request, "ver_proceso.html", {
        "sector": sector,
        "instructivo": instructivo,
        "usuarios_con_perfil": usuarios_con_perfil
    })




logger = logging.getLogger(__name__)

@login_required
def firmar_proceso(request, proceso_id):
    """
    Permite al usuario firmar digitalmente un instructivo general y avanzar al siguiente.
    """
    proceso = get_object_or_404(InstructivoGeneral, id=proceso_id)

    if request.method == "POST":
        if request.user not in proceso.firmado_por.all():
            proceso.firmado_por.add(request.user)
            proceso.save()

        # Obtener instructivos pendientes que el usuario no ha firmado
        instructivos_pendientes = InstructivoGeneral.objects.filter(
            sector__in=request.user.sectores.all()
        ).exclude(firmado_por=request.user).order_by('id')

        # Si quedan instructivos por firmar, redirigir al siguiente
        if instructivos_pendientes.exists():
            siguiente_proceso = instructivos_pendientes.first()
            return redirect('ver_procesos', sector_id=siguiente_proceso.sector.id)

        # Si todos fueron firmados, ir al home
        return redirect('home')

    return redirect('ver_procesos', sector_id=proceso.sector.id)



User = get_user_model()

@loading_view
@login_required
def lista_usuarios(request):
    """Carga la plantilla de usuarios para mostrar todos los usuarios registrados o hacer búsquedas."""
    usuarios = User.objects.all()
    return render(request, 'usuarios.html', {'usuarios': usuarios})

@login_required
def buscar_usuarios(request):
    """Busca usuarios por varios campos o retorna los más recientes si no hay búsqueda."""
    query = request.GET.get('q', '').strip()

    if query:
        # Concatenar first_name y last_name para búsquedas combinadas
        usuarios = User.objects.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField())
        ).filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(full_name__icontains=query)  # Buscar en el nombre completo concatenado
        ).distinct()
    else:
        # Return-- > result
        # Retornar los usuarios más recientes
        usuarios = User.objects.all().order_by('-date_joined')[:10]

    results = [
        {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'sector': user.sectores.first().nombre if user.sectores.exists() else "Sin asignar",
        }
        for user in usuarios
    ]
    return JsonResponse({'results': results})


@login_required
def actualizar_usuario(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu información se ha actualizado correctamente.")
            return redirect('actualizar_usuario')
        else:
            messages.error(request, "Ocurrió un error al actualizar tu información.")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'actualizar_usuario.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def gestionar_permisos_usuario(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        # Verificar si los datos provienen del formulario o son JSON
        if request.content_type == "application/json":
            # Procesar asignación de sectores (JSON)
            try:
                data = json.loads(request.body)
                assigned_sector_ids = data.get("assigned_sector_ids", [])
                assigned_sectors = Sector.objects.filter(id__in=assigned_sector_ids)
                user.sectores.set(assigned_sectors)
                return JsonResponse({"status": "success"})
            except json.JSONDecodeError:
                return JsonResponse({"status": "error", "message": "Formato JSON no válido."}, status=400)
        else:
            # Procesar datos del formulario
            if "update_info" in request.POST:
                user.first_name = request.POST.get("first_name", user.first_name)
                user.last_name = request.POST.get("last_name", user.last_name)
                user.email = request.POST.get("email", user.email)
                user.username = request.POST.get("username", user.username)
                user.save()
                messages.success(request, "Información del usuario actualizada correctamente.")
            elif "change_password" in request.POST:
                new_password = request.POST.get("new_password")
                if new_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Contraseña actualizada correctamente.")
                else:
                    messages.error(request, "La contraseña no puede estar vacía.")
            return redirect("gestionar_permisos_usuario", user_id=user_id)

    all_sectors = Sector.objects.all()
    assigned_sectors = user.sectores.all()

    return render(
        request,
        "permisos.html",
        {
            "user": user,
            "all_sectors": all_sectors,
            "assigned_sectors": [s.nombre.lower() for s in assigned_sectors],
        },
    )


@require_POST
@login_required
def update_user_sector(request):
    """Actualiza los sectores del usuario mediante AJAX y envía notificaciones si es necesario."""
    data = json.loads(request.body)
    user_id = data.get("user_id")
    sector_id = data.get("sector_id")
    action = data.get("action")

    user = get_object_or_404(User, id=user_id)
    sector = get_object_or_404(Sector, id=sector_id)

    if action == "add":
        # Agregar permiso de sector y enviar notificación
        codename = f'permiso_{sector.nombre.lower()}'
        sector_permission, created = Permission.objects.get_or_create(codename=codename, name=f"Permiso para {sector.nombre}")
        user.user_permissions.add(sector_permission)

        # Crear notificación
        Notificacion.objects.create(
            tarea=None,
            titulo="Proceso empresarial",
            mensaje=f"Debe firmar el proceso empresarial de {sector.nombre}.",
            hora_envio=timezone.now()
        )

        return JsonResponse({"status": "success", "sector_name": sector.nombre})

    elif action == "remove":
        # Quitar permiso de sector
        codename = f'permiso_{sector.nombre.lower()}'
        sector_permission = Permission.objects.filter(codename=codename).first()
        if sector_permission:
            user.user_permissions.remove(sector_permission)
        return JsonResponse({"status": "success", "sector_name": sector.nombre})

    return JsonResponse({"status": "error", "message": "Acción no válida"})

@login_required
@require_http_methods(["POST"])
def update_sectors(request):
    data = json.loads(request.body)
    user_id = data.get("user_id")
    sector_id = data.get("sector_id")
    action = data.get("action")

    user = get_object_or_404(CustomUser, id=user_id)
    sector = get_object_or_404(Sector, id=sector_id)

    if action == "add":
        user.sector.add(sector)  # Añadir sector al usuario
        user.save()
        message = f"Sector {sector.nombre} asignado."
    elif action == "remove":
        user.sector.remove(sector)  # Quitar sector del usuario
        user.save()
        message = f"Sector {sector.nombre} eliminado."

    return JsonResponse({"status": "success", "message": message, "action": action})

@loading_view
@login_required
def comunicacion_interna(request):
    """
    Vista para mostrar la plantilla de comunicación interna con solicitudes pendientes.
    """
    solicitudes = SolicitudTarea.objects.filter(destinatario=request.user, estado='pendiente')
    return render(request, 'comunicacion_interna.html', {'solicitudes': solicitudes})

User = get_user_model()

@login_required
def enviar_solicitud_tarea(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            destinatario_id = data.get('destinatario_id')
            descripcion = data.get('descripcion', '').strip()
            fecha_finalizacion = data.get('fecha_finalizacion')

            if not destinatario_id or not descripcion or not fecha_finalizacion:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios'})

            destinatario = get_object_or_404(User, id=destinatario_id)

            # Crear la solicitud
            SolicitudTarea.objects.create(
                solicitante=request.user,
                destinatario=destinatario,
                descripcion=descripcion,
                fecha_finalizacion=fecha_finalizacion
            )

            # Enviar notificación
            enviar_notificacion_tarea.delay(
                solicitante=request.user.username,
                destinatario_id=destinatario.id,
                descripcion=descripcion
            )

            return JsonResponse({'status': 'success', 'message': 'Solicitud enviada correctamente'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@login_required
def listar_solicitudes(request):
    """Lista las solicitudes recibidas y enviadas por el usuario actual."""
    solicitudes_recibidas = SolicitudTarea.objects.filter(destinatario=request.user, estado='pendiente')
    solicitudes_enviadas = SolicitudTarea.objects.filter(solicitante=request.user)

    return render(request, 'solicitudes_tareas.html', {
        'solicitudes_recibidas': solicitudes_recibidas,
        'solicitudes_enviadas': solicitudes_enviadas
    })


@login_required
def solicitudes_pendientes(request):
    """
    Retorna las solicitudes pendientes del usuario logueado.
    """
    solicitudes = SolicitudTarea.objects.filter(destinatario=request.user, estado='pendiente')
    results = [
        {
            'id': solicitud.id,  # Agregamos la ID para que esté disponible en el frontend
            'solicitante': f"{solicitud.solicitante.first_name} {solicitud.solicitante.last_name}",
            'descripcion': solicitud.descripcion,
            'fecha_finalizacion': solicitud.fecha_finalizacion.strftime('%d/%m/%Y')
        }
        for solicitud in solicitudes
    ]
    return JsonResponse({'results': results})

@login_required
def aceptar_solicitud(request, solicitud_id):
    """
    Acepta una solicitud, cambia su estado a 'En curso' y redirige al panel de gestión de la tarea.
    """
    solicitud = get_object_or_404(SolicitudTarea, id=solicitud_id, destinatario=request.user)
    
    if solicitud.estado != 'pendiente':
        return JsonResponse({'status': 'error', 'message': 'La solicitud ya fue procesada.'})

    solicitud.estado = 'en curso'
    solicitud.save()

    # Redirigir al panel de gestión de la tarea
    return redirect('gestionar_tarea', tarea_id=solicitud.id)

@login_required
def gestionar_tarea(request, tarea_id):
    """
    Muestra el panel para gestionar una tarea.
    Permite acceder si el usuario es el destinatario o el solicitante,
    asegurando que pueda interactuar con los datos y agregar comentarios.
    """
    tarea = get_object_or_404(
        SolicitudTarea,
        Q(id=tarea_id) & (Q(destinatario=request.user) | Q(solicitante=request.user))
    )

    return render(request, 'gestionar_tarea.html', {
        'tarea': tarea
    })

@login_required
def actualizar_tarea(request, tarea_id):
    if request.method == "POST":
        try:
            # Permitir acceso al destinatario o solicitante
            tarea = get_object_or_404(
                SolicitudTarea,
                Q(id=tarea_id) & (Q(destinatario=request.user) | Q(solicitante=request.user))
            )
            data = json.loads(request.body)

            # Validar y convertir los datos recibidos
            descripcion = data.get("descripcion", "").strip()
            fecha_finalizacion_str = data.get("fecha_finalizacion", None)
            estado = data.get("estado", None)

            # Convertir fecha_finalizacion a un objeto date
            if fecha_finalizacion_str:
                try:
                    fecha_finalizacion = datetime.strptime(fecha_finalizacion_str, "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"status": "error", "message": "Formato de fecha inválido."})
            else:
                fecha_finalizacion = tarea.fecha_finalizacion  # Mantener la fecha existente si no se envía

            # Validar los campos antes de guardar
            if not descripcion or not estado:
                return JsonResponse({"status": "error", "message": "Datos incompletos."})

            # Actualizar los datos de la tarea
            tarea.descripcion = descripcion
            tarea.fecha_finalizacion = fecha_finalizacion
            tarea.estado = estado
            tarea.save()

            # Respuesta JSON con datos actualizados
            return JsonResponse({
                "status": "success",
                "tarea": {
                    "descripcion": tarea.descripcion,
                    "fecha_finalizacion": tarea.fecha_finalizacion.strftime("%Y-%m-%d"),
                    "estado_display": tarea.get_estado_display(),
                }
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error al actualizar: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Método no permitido."})

@login_required
def finalizar_tarea(request, tarea_id):
    if request.method == "POST":
        try:
            tarea = get_object_or_404(SolicitudTarea, id=tarea_id, destinatario=request.user)

            # Cambiar el estado de la tarea a "finalizada"
            tarea.estado = "finalizada"
            tarea.fecha_finalizacion = date.today()  # Registrar la fecha actual como fecha de finalización
            tarea.save()

            return JsonResponse({"status": "success", "message": "Tarea finalizada correctamente."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Error al finalizar la tarea: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Método no permitido."})

@login_required
def posponer_solicitud(request, solicitud_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        motivo = data.get('motivo', '').strip()

        # Depuración
        print(f"Solicitud ID: {solicitud_id}, Motivo: {motivo}")

        if not motivo:
            return JsonResponse({'status': 'error', 'message': 'El motivo es obligatorio.'})

        try:
            solicitud = SolicitudTarea.objects.get(id=solicitud_id, destinatario=request.user)
        except SolicitudTarea.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Solicitud no encontrada.'})

        if solicitud.estado != 'pendiente':
            return JsonResponse({'status': 'error', 'message': 'La solicitud no está en estado pendiente.'})

        solicitud.estado = 'rechazada'
        solicitud.motivo_rechazo = motivo
        solicitud.save()

        return JsonResponse({'status': 'success', 'message': 'Solicitud Rechazada correctamente.'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})


@login_required
def crear_comentario(request, tarea_id):
    if request.method == "POST":
        try:
            # Permitir acceso al destinatario o solicitante
            tarea = get_object_or_404(
                SolicitudTarea, 
                Q(id=tarea_id) & (Q(destinatario=request.user) | Q(solicitante=request.user))
            )
            data = json.loads(request.body)

            texto = data.get("texto", "").strip()
            if not texto:
                return JsonResponse({"status": "error", "message": "El comentario no puede estar vacío."})

            comentario = Comentario.objects.create(
                tarea=tarea,
                usuario=request.user,
                texto=texto,
            )

            return JsonResponse({
                "status": "success",
                "comentario": {
                    "id": comentario.id,
                    "usuario": request.user.get_full_name(),
                    "texto": comentario.texto,
                    "fecha_creacion": comentario.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                }
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Método no permitido."})

@login_required
def editar_comentario(request, comentario_id):
    if request.method == "POST":
        try:
            comentario = get_object_or_404(Comentario, id=comentario_id, usuario=request.user)
            data = json.loads(request.body)

            texto = data.get("texto", "").strip()
            if not texto:
                return JsonResponse({"status": "error", "message": "El comentario no puede estar vacío."})

            comentario.texto = texto
            comentario.save()

            return JsonResponse({"status": "success", "message": "Comentario actualizado correctamente."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Método no permitido."})


@login_required
def eliminar_comentario(request, comentario_id):
    if request.method == "POST":
        try:
            comentario = get_object_or_404(Comentario, id=comentario_id, usuario=request.user)
            comentario.delete()
            return JsonResponse({"status": "success", "message": "Comentario eliminado correctamente."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Método no permitido."})

@loading_view
@login_required
def home(request):
    # Obtener los sectores del usuario logueado
    sectores_usuario = request.user.sectores.all()

    # Fecha del día anterior
    dia_anterior = date.today() - timedelta(days=1)

    # Filtrar tareas finalizadas el día anterior relacionadas a los sectores del usuario
    tareas_finalizadas = SolicitudTarea.objects.filter(
        estado='finalizada',
        fecha_finalizacion=dia_anterior,
        destinatario__sectores__in=sectores_usuario
    ).values(
        'destinatario__id', 'destinatario__first_name', 'destinatario__last_name', 'destinatario__sectores__nombre'
    ).annotate(
        total_tareas=Count('id')
    ).order_by('-total_tareas')[:5]  # Limitar a los 5 usuarios con más tareas

    # Filtrar tareas por estado para el usuario logueado
    tareas_pendientes = SolicitudTarea.objects.filter(destinatario=request.user, estado="pendiente")
    tareas_en_curso = SolicitudTarea.objects.filter(destinatario=request.user, estado="en curso")
    tareas_finalizadas_usuario = SolicitudTarea.objects.filter(destinatario=request.user, estado="finalizada")

    return render(request, 'home.html', {
        'tareas_pendientes': tareas_pendientes,
        'tareas_en_curso': tareas_en_curso,
        'tareas_finalizadas_usuario': tareas_finalizadas_usuario,
        'ranking_tareas_finalizadas': tareas_finalizadas,  # Datos para la tabla de usuarios
    })

@login_required
def medir_tiempo(request):
    
    return render(request, 'medir_tiempo.html')

@loading_view
@login_required
def perfil_usuario(request, user_id):
    from django.utils.translation import gettext as _

    # Diccionario de traducción para los días de la semana
    dias_traduccion = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    # Obtener el usuario objetivo
    user = get_object_or_404(CustomUser, id=user_id)

    # Indicadores de rendimiento
    total_tareas_completadas = SolicitudTarea.objects.filter(destinatario=user, estado="finalizada").count()
    total_tareas_pendientes = SolicitudTarea.objects.filter(destinatario=user, estado="pendiente").count()
    total_tareas = total_tareas_completadas + total_tareas_pendientes
    eficiencia = round((total_tareas_completadas / total_tareas) * 100, 2) if total_tareas > 0 else 0

    # Historial de tareas
    historial_tareas = SolicitudTarea.objects.filter(destinatario=user).order_by('-fecha_finalizacion')

    # Análisis de patrones de conducta
    tareas_finalizadas = SolicitudTarea.objects.filter(destinatario=user, estado="finalizada")
    dias_productividad = tareas_finalizadas.values_list('fecha_finalizacion', flat=True)

    # Día más productivo (traducido al español)
    dias_contados = Counter([dia.strftime('%A') for dia in dias_productividad])
    dia_mas_productivo_en = dias_contados.most_common(1)[0][0] if dias_contados else "No disponible"
    dia_mas_productivo = dias_traduccion.get(dia_mas_productivo_en, "No disponible")

    # Hora pico de actividad
    horas_productividad = tareas_finalizadas.annotate(hora=F('fecha_creacion__hour')).values_list('hora', flat=True)
    hora_pico = Counter(horas_productividad).most_common(1)[0][0] if horas_productividad else None
    rango_hora_pico = f"{hora_pico}:00 - {hora_pico + 1}:00" if hora_pico is not None else "No disponible"

    # Tarea más común
    tarea_mas_comun = tareas_finalizadas.values('descripcion').annotate(total=Count('id')).order_by('-total').first()
    tarea_mas_comun = tarea_mas_comun['descripcion'] if tarea_mas_comun else "No disponible"

    # Datos para el gráfico de actividad
    dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    tareas_por_dia = {dia: 0 for dia in dias_semana}
    for dia in dias_productividad:
        dia_nombre = dia.strftime('%A')
        tareas_por_dia[dia_nombre] += 1
    tareas_grafico = [tareas_por_dia[dia] for dia in dias_semana]

    return render(request, 'perfil_usuario.html', {
        'user': user,
        'tareas': historial_tareas,
        'indicadores': {
            'completadas': total_tareas_completadas,
            'pendientes': total_tareas_pendientes,
            'eficiencia': eficiencia,
        },
        'patrones': {
            'dia_mas_productivo': dia_mas_productivo,
            'hora_pico': rango_hora_pico,
            'tarea_mas_comun': tarea_mas_comun,
        },
        'grafico_datos': tareas_grafico,
    })

@loading_view
@login_required
def solicitudes_enviadas(request):
    # Obtener todas las solicitudes enviadas por el usuario logueado
    solicitudes = SolicitudTarea.objects.filter(solicitante=request.user).order_by('-fecha_creacion')

    # Filtrar por búsqueda si hay un query
    query = request.GET.get('q', '').strip()
    if query:
        solicitudes = solicitudes.filter(
            Q(destinatario__first_name__icontains=query) |
            Q(destinatario__last_name__icontains=query) |
            Q(estado__icontains=query)
        )

    # Paginación
    paginator = Paginator(solicitudes, 10)  # 10 solicitudes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'solicitudes_enviadas.html', {
        'solicitudes': page_obj,
        'query': query,
    })

@login_required
def cancelar_solicitud(request, solicitud_id):
    if request.method == "POST":
        solicitud = get_object_or_404(SolicitudTarea, id=solicitud_id, solicitante=request.user, estado="pendiente")
        solicitud.delete()  # Eliminar la solicitud
        messages.success(request, "La solicitud fue cancelada correctamente.")
    return redirect('solicitudes_enviadas')

@login_required
def panel_empresa(request):
    
    return render(request, 'panel_empresa.html')




@loading_view
@login_required
def productividad_sector(request):
    sector = request.GET.get('sector', 'general')
    filtro_sector = {} if sector == 'general' else {'destinatario__sectores__nombre': sector}

    total_tareas = SolicitudTarea.objects.filter(**filtro_sector).count()
    tareas_finalizadas = SolicitudTarea.objects.filter(**filtro_sector, estado='finalizada').count()

    productividad = [
        int((tareas_finalizadas / total_tareas * 100) if total_tareas > 0 else 0),  # Alta
        int(((total_tareas - tareas_finalizadas) / total_tareas * 100) if total_tareas > 0 else 0),  # Media
        0  # Baja
    ]

    return JsonResponse({'productividad': productividad})

@login_required
def tareas_largas_view(request):
    # Obtener el sector seleccionado desde los parámetros GET
    sector = request.GET.get('sector', 'general')
    filtro_sector = {} if sector == 'general' else {'sector__nombre': sector}

    # Obtener el mes actual
    mes_actual = date.today().month

    # Filtrar tareas por sector y calcular cuántas veces fueron finalizadas en el mes actual
    tareas_largas = Tarea.objects.filter(**filtro_sector).annotate(
        realizaciones_mes=Count(
            'procesos__tareas',  # Asumimos que las tareas están relacionadas a procesos finalizados
            filter=Q(procesos__tareas__fecha_vencimiento__month=mes_actual, procesos__tareas__estado='finalizada')
        )
    ).values(
        'nombre', 'realizaciones_mes'
    )

    # Retornar datos en formato JSON
    return JsonResponse({'tareas': list(tareas_largas)})

@login_required
def usuarios_menos_productivos_view(request):
    sector = request.GET.get('sector', 'general')
    filtro_sector = {} if sector == 'general' else {'sector__nombre': sector}

    usuarios_menos_productivos = (
        Tarea.objects.filter(**filtro_sector, estado__in=['pendiente', 'en curso'])
        .values('destinatario__first_name', 'destinatario__last_name')
        .annotate(total_tareas=Count('id'))
        .order_by('-total_tareas')[:5]
    )

    return JsonResponse({'usuarios': list(usuarios_menos_productivos)})
