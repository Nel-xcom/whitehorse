# Generated by Django 5.1.5 on 2025-02-10 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_instructivogeneral'),
    ]

    operations = [
        migrations.AlterField(
            model_name='procesoempresarial',
            name='tipo',
            field=models.CharField(choices=[('IT', 'Instructivo de Trabajo'), ('IC', 'Instructivo de Calidad')], default='IT', max_length=2),
        ),
    ]
