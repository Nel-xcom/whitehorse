# Generated by Django 5.1.5 on 2025-02-11 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_rename_descripcion_sector_procesoempresarial_alcance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructivogeneral',
            name='logo_empresa',
            field=models.ImageField(blank=True, null=True, upload_to='logos/'),
        ),
    ]
