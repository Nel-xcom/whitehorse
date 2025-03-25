"""generic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Especificamos el template aquí
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('perfil/<int:user_id>/', views.perfil_usuario, name='perfil_usuario'),
    
    path('seleccionar_sector/', views.seleccionar_sector, name='seleccionar_sector'),
    path('ver_procesos/<int:sector_id>/', views.ver_procesos, name='ver_procesos'),
    path('actualizar_sectores/', views.actualizar_sectores, name='actualizar_sectores'),
    path('actualizar_sectores/', views.actualizar_sectores, name='actualizar_sectores'),
    path('procesos/<int:proceso_id>/firmar/', views.firmar_proceso, name='firmar_proceso'),


    path('agregar-sector/', views.agregar_sector, name='agregar_sector'),
    path('borrar-sector/<int:sector_id>/', views.borrar_sector, name='borrar_sector'),

    path('sectores/<int:sector_id>/tareas/', views.gestion_tareas, name='gestion_tareas'),
    path('tareas/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('borrar-tarea/<int:tarea_id>/', views.borrar_tarea, name='borrar_tarea'),
    
    path('tareas/<int:tarea_id>/notificacion/', views.actualizar_notificacion, name='actualizar_notificacion'),
    path('tareas/<int:tarea_id>/notificaciones/', views.gestionar_notificaciones, name='gestionar_notificaciones'),
    path('notificaciones/marcar-todas-como-leidas/', views.marcar_todas_como_leidas, name='marcar_todas_como_leidas'),

    path('sectores/<int:sector_id>/actualizar_logo/', views.actualizar_logo, name='actualizar_logo'),
    path('usuarios/update_sectors/', views.update_user_sector, name='update_user_sector'),
    path('usuarios/update_sectors/', views.update_sectors, name='update_sectors'),

    path('sectores/<int:sector_id>/procesos/', views.procesos_digitales, name='procesos_digitales'),
    path('sectores/<int:sector_id>/crear/<str:tipo_proceso>/', views.crear_proceso, name='crear_proceso'),
    path('procesos/<int:proceso_id>/eliminar/', views.eliminar_proceso, name='eliminar_proceso'),
    path("sectores/<int:sector_id>/editar_proceso/<str:tipo_proceso>/<int:proceso_id>/", views.editar_proceso, name="editar_proceso"),
    path("sectores/<int:sector_id>/editar_proceso/<str:tipo_proceso>/", views.editar_proceso, name="editar_proceso_sin_id"),

    path('api/tareas/', views.obtener_tareas_por_sector, name='api_tareas'),
    path('api/tareas/', views.api_tareas, name='api_tareas'),
    path('api/guardar_orden_tareas/', views.guardar_orden_tareas, name='guardar_orden_tareas'),
    path('flujos_trabajo/proceso/', views.proceso_flujo_trabajo, name='proceso_flujo_trabajo'),
    path('flujos_trabajo/guardar/', views.guardar_flujo_trabajo, name='guardar_flujo_trabajo'),
    path('api/usuarios_por_tarea/', views.api_usuarios_por_tarea, name='api_usuarios_por_tarea'),

    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('usuario/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),
    path('usuarios/<int:user_id>/permisos/', views.gestionar_permisos_usuario, name='gestionar_permisos_usuario'),

    path('comunicacion-interna/', views.comunicacion_interna, name='comunicacion_interna'),
    path('comunicacion-interna/buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('solicitar-tarea/', views.enviar_solicitud_tarea, name='enviar_solicitud_tarea'),
    path('solicitudes-tareas/', views.listar_solicitudes, name='listar_solicitudes'),
    path('comunicacion-interna/solicitudes-pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('solicitudes/<int:solicitud_id>/aceptar/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('tareas/<int:tarea_id>/gestionar/', views.gestionar_tarea, name='gestionar_tarea'),
    path('tareas/<int:tarea_id>/actualizar/', views.actualizar_tarea, name='actualizar_tarea'),
    path('solicitudes/<int:solicitud_id>/posponer/', views.posponer_solicitud, name='posponer_solicitud'),
    path('solicitudes-enviadas/', views.solicitudes_enviadas, name='solicitudes_enviadas'),
    path('solicitudes/<int:solicitud_id>/cancelar/', views.cancelar_solicitud, name='cancelar_solicitud'),

    path('tareas/<int:tarea_id>/comentarios/crear/', views.crear_comentario, name='crear_comentario'),
    path('comentarios/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentarios/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),
    path('tareas/<int:tarea_id>/finalizar/', views.finalizar_tarea, name='finalizar_tarea'),

    path('panel-empresa/', views.panel_empresa, name='panel_empresa'),
    path('empresa/tareas-largas/', views.tareas_largas_view, name='tareas_largas'),

    path('home/', views.home, name='home'),

    path('mediciones/', views.medir_tiempo, name='mediciones'),
    path('empresa/productividad/', views.productividad_sector, name='productividad_sector'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
