# Generated by Django 5.0.14 on 2025-05-28 15:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cama',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='IdCama')),
                ('codcama', models.CharField(max_length=255, verbose_name='Código de Cama')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')),
                ('Ups', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='camas', to='api.ups', verbose_name='UPS')),
                ('estadocama', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='camas', to='api.estadocama', verbose_name='Estado de Cama')),
                ('ipress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='camas', to='api.ipress', verbose_name='Ipress')),
                ('tipocama', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='camas', to='api.tipocama', verbose_name='Tipo de Cama')),
            ],
            options={
                'verbose_name': 'Cama',
                'verbose_name_plural': 'Camas',
                'ordering': ['codcama'],
            },
        ),
    ]
