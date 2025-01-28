# Generated by Django 5.1.5 on 2025-01-27 21:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vineyards', '0004_cellar_tank'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CrushedJuiceAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allocated_volume', models.FloatField(help_text='Volume allocated to this tank in liters')),
                ('allocation_date', models.DateField(help_text='Date of allocation')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the allocation', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('harvest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='vineyards.harvest')),
                ('tank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='vineyards.tank')),
            ],
        ),
    ]
