# Generated by Django 5.1.1 on 2024-11-16 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='sector',
        ),
        migrations.AddField(
            model_name='customuser',
            name='sectores',
            field=models.ManyToManyField(blank=True, related_name='usuarios', to='core.sector'),
        ),
    ]
