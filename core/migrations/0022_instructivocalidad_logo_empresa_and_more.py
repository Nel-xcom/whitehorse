# Generated by Django 5.1.5 on 2025-02-13 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_instructivogeneral_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructivocalidad',
            name='logo_empresa',
            field=models.ImageField(blank=True, null=True, upload_to='logos/'),
        ),
        migrations.AddField(
            model_name='instructivotrabajo',
            name='logo_empresa',
            field=models.ImageField(blank=True, null=True, upload_to='logos/'),
        ),
    ]
