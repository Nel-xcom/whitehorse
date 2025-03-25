from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import date
from django.core.exceptions import ValidationError

class Sector(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

@receiver(post_save, sender=Sector)
def crear_permiso_para_sector(sender, instance, created, **kwargs):
    content_type = ContentType.objects.get_for_model(Sector)
    codename = f'permiso_{instance.nombre.lower()}'
    if not Permission.objects.filter(codename=codename).exists():
        Permission.objects.create(
            codename=codename,
            name=f'Permiso para el sector {instance.nombre}',
            content_type=content_type
        )

class CustomUser(AbstractUser):
    # Relación directa con Sector para indicar al sector del usuario
    sectores = models.ManyToManyField(Sector, related_name='usuarios', blank=True)
    
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name=('groups'),
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text=('Specific permissions for this user.'),
        verbose_name=('user permissions'),
    )

User = get_user_model()

class PerfilPuesto(models.Model):
    """
    Modelo que define los perfiles de puesto dentro de cada sector.
    """
    sector = models.ForeignKey(Sector, related_name='perfiles', on_delete=models.CASCADE)
    nombre_puesto = models.CharField(max_length=150)
    descripcion = models.TextField()
    responsable = models.ForeignKey(User, related_name='puestos', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre_puesto} - {self.sector.nombre}"


class InstructivoGeneral(models.Model):
    nombre = models.CharField(max_length=150, unique=True, default="No definido")
    sector = models.OneToOneField(Sector, related_name='instructivo_general', on_delete=models.CASCADE)
    descripcion_sector = models.TextField(blank=True)
    logo_empresa = models.ImageField(upload_to='logos/', blank=True, null=True)
    firmado_por = models.ManyToManyField("CustomUser", related_name="firmas_instructivos_generales", blank=True)


    def __str__(self):
        return f"Instructivo General - {self.sector.nombre}"


class Tarea(models.Model):
    # Opciones de estado
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Curso', 'En Curso'),
        ('Finalizada', 'Finalizada'),
    ]

    # Opciones de notificación
    NOTIFICACION_CHOICES = [
        ('Programadas', 'Programadas'),
        ('Automaticas', 'Automaticas'),
    ]

    # ✅ Opciones de prioridad
    PRIORIDAD_CHOICES = [
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
    ]

    # Campos principales
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Pendiente")
    fecha_creacion = models.DateTimeField(default=now)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    sector = models.ForeignKey(Sector, related_name='tareas', on_delete=models.CASCADE)
    notificacion = models.CharField(max_length=20, choices=NOTIFICACION_CHOICES, default='Programadas')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default="Media")
    responsable = models.ForeignKey(CustomUser, related_name='tareas_asignadas', on_delete=models.SET_NULL, null=True, blank=True)
    tiempo_dedicado = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def calcular_tiempo_dedicado(self):
        """
        Calcula el tiempo dedicado en horas, considerando la diferencia entre la fecha de finalización y creación.
        Si la tarea aún no ha finalizado, devuelve 0.
        """
        if self.fecha_vencimiento and self.fecha_creacion:
            tiempo_total = self.fecha_vencimiento - self.fecha_creacion.date()
            return round(tiempo_total.days * 24, 2)  # Convertir días a horas
        return 0.00

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular el tiempo dedicado automáticamente al guardar la tarea.
        """
        if self.estado == 'Finalizada':
            self.tiempo_dedicado = self.calcular_tiempo_dedicado()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
    
class FlujoTrabajo(models.Model):
    nombre = models.CharField(max_length=150)
    sector = models.ForeignKey('Sector', on_delete=models.CASCADE)
    tareas = models.ManyToManyField('Tarea', through='FlujoTarea')

    def __str__(self):
        return self.nombre

class FlujoTarea(models.Model):
    flujo = models.ForeignKey(FlujoTrabajo, on_delete=models.CASCADE)
    tarea = models.ForeignKey('Tarea', on_delete=models.CASCADE)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # <- Cambio aquí
    orden = models.PositiveIntegerField()


class ProcesoEmpresarial(models.Model):
    TIPO_CHOICES = [
        ('IT', 'Instructivo de Trabajo'),
        ('IC', 'Instructivo de Calidad'),
    ]

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default='IT')
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Permite valores nulos para evitar conflictos en la migración
    version = models.PositiveIntegerField(default=1)
    fecha_emision = models.DateField(default=timezone.now)  # Permite definir la fecha manualmente
    objetivo = models.TextField(blank=True, null=True)
    alcance = models.TextField(blank=True, null=True)
    responsabilidades = models.TextField(blank=True, null=True)
    pasos = models.TextField(blank=True, null=True)
    equipo_requerido = models.TextField(blank=True, null=True)
    medidas_seguridad = models.TextField(blank=True, null=True)

    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="procesos_empresariales")

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    def save(self, *args, **kwargs):
        """
        Control de versión: Si se modifica el alcance o las responsabilidades, 
        se incrementa la versión automáticamente.
        """
        if self.pk:
            original = ProcesoEmpresarial.objects.get(pk=self.pk)
            if original.alcance != self.alcance or original.responsabilidades != self.responsabilidades:
                self.version += 1

        super().save(*args, **kwargs)


class BaseInstructivo(models.Model):
    logo_empresa = models.ImageField(upload_to='logos/', blank=True, null=True)
    nombre = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(max_length=50, unique=True)
    version = models.PositiveIntegerField(default=1)
    fecha_revision = models.DateField(auto_now=True)
    objetivo = models.TextField()
    alcance = models.TextField()
    responsabilidades = models.TextField()
    pasos = models.TextField()

    sector = models.ForeignKey(Sector, related_name='todos_instructivos', on_delete=models.CASCADE)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructivos_creados")
    firmado_por = models.ManyToManyField(User, related_name='firmas_generales_instructivos', blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} (v{self.version})"

class InstructivoTrabajo(BaseInstructivo):
    equipo_requerido = models.TextField(blank=True, null=True)
    medidas_seguridad = models.TextField(blank=True, null=True)

    # Agregamos `related_name` únicos para evitar conflictos
    sector = models.ForeignKey(Sector, related_name='instructivos_trabajo', on_delete=models.CASCADE)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructivos_trabajo_creados")
    firmado_por = models.ManyToManyField(User, related_name='firmas_instructivos_trabajo', blank=True)

    class Meta:
        verbose_name = "Instructivo de Trabajo"
        verbose_name_plural = "Instructivos de Trabajo"

class InstructivoCalidad(BaseInstructivo):
    criterios_evaluacion = models.TextField()
    normativa_asociada = models.TextField(blank=True, null=True)

    # Agregamos `related_name` únicos para evitar conflictos
    sector = models.ForeignKey(Sector, related_name='instructivos_calidad', on_delete=models.CASCADE)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructivos_calidad_creados")
    firmado_por = models.ManyToManyField(User, related_name='firmas_instructivos_calidad', blank=True)

    class Meta:
        verbose_name = "Instructivo de Calidad"
        verbose_name_plural = "Instructivos de Calidad"

class Notificacion(models.Model):
    DIAS_CHOICES = [
        ('todos', 'Todos los días'),
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miércoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sábado', 'Sábado'),
    ]

    tarea = models.ForeignKey(Tarea, related_name='notificaciones', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    dia = models.CharField(max_length=10, choices=DIAS_CHOICES, default='todos')
    hora_envio = models.TimeField()
    enviar_ahora = models.BooleanField(default=False)
    leida = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Notificación para {self.tarea.nombre} - {self.titulo}"
    
User = get_user_model()

class SolicitudTarea(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]

    solicitante = models.ForeignKey(User, related_name='solicitudes_enviadas', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, related_name='solicitudes_recibidas', on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateField(default=date.today)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    motivo_rechazo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Solicitud de {self.solicitante} a {self.destinatario}"


class Mensaje(models.Model):
    remitente = models.ForeignKey(CustomUser, related_name='mensajes_enviados', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(CustomUser, related_name='mensajes_recibidos', on_delete=models.CASCADE)
    contenido = models.TextField(blank=True)
    archivo = models.FileField(upload_to='mensajes/', blank=True, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.remitente} a {self.destinatario}"
    

class Comentario(models.Model):
    tarea = models.ForeignKey('SolicitudTarea', related_name='comentarios', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, related_name='comentarios', on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.tarea.descripcion}"