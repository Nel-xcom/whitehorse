# Generated by Django 5.1.5 on 2025-02-13 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_instructivogeneral_logo_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructivogeneral',
            name='nombre',
            field=models.CharField(default='No definido', max_length=150, unique=True),
        ),
    ]
