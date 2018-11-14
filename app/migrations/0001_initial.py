# Generated by Django 2.1.2 on 2018-10-04 18:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Memoria',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tamaño', models.IntegerField(verbose_name='Tamaño (KB)')),
                ('esquema', models.CharField(max_length=30, verbose_name='Esquema')),
                ('particiones', models.TextField(blank=True, null=True, verbose_name='Particiones')),
                ('algoritmo_colocacion', models.CharField(max_length=30, verbose_name='Tipo')),
            ],
            options={
                'verbose_name': 'Memoria',
                'verbose_name_plural': 'Memorias',
            },
        ),
        migrations.CreateModel(
            name='Proceso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='PID')),
                ('tiempo_arribo', models.IntegerField(verbose_name='Tiempo de arribo')),
                ('tiempo_recursos', models.TextField(blank=True, null=True, verbose_name='Tiempo de recursos')),
            ],
            options={
                'verbose_name': 'Proceso',
                'verbose_name_plural': 'Procesos',
            },
        ),
        migrations.CreateModel(
            name='Simulacion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('algoritmo_planificacion', models.CharField(max_length=30)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('memoria', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Memoria')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Simulación',
                'verbose_name_plural': 'Simulaciones',
            },
        ),
        migrations.AddField(
            model_name='proceso',
            name='simulacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Procesos', to='app.Simulacion', verbose_name='Simulación'),
        ),
    ]