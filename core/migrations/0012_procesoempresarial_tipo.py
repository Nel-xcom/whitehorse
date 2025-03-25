# Generated by Django 5.1.1 on 2025-01-06 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_tarea_fecha_creacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='procesoempresarial',
            name='tipo',
            field=models.CharField(choices=[('IG', 'Instructivo General'), ('IT', 'Instructivo de Trabajo'), ('IC', 'Instructivo de Calidad')], default='IT', max_length=2),
        ),
    ]
