# Generated by Django 5.1.1 on 2024-11-28 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_solicitudtarea_fecha_finalizacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudtarea',
            name='motivo_rechazo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
