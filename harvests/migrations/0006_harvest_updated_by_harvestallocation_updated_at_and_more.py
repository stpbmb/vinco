# Generated by Django 5.1.5 on 2025-02-01 14:42

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cellars', '0006_alter_tank_created_by_alter_tank_tank_type'),
        ('harvests', '0005_alter_harvest_options_alter_harvest_date_and_more'),
        ('vineyards', '0014_alter_supplier_options_alter_vineyard_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='harvest',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='harvest_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='harvestallocation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='harvestallocation',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='harvest_allocation_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='harvest_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='juice_yield',
            field=models.IntegerField(default=75, help_text='Juice yield in absolute numbers (e.g., 75 for 75%)', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='quantity',
            field=models.DecimalField(decimal_places=2, help_text='Quantity of grapes harvested in kilograms', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='harvest',
            name='vineyard',
            field=models.ForeignKey(help_text='Vineyard where grapes were harvested', on_delete=django.db.models.deletion.PROTECT, related_name='harvests', to='vineyards.vineyard'),
        ),
        migrations.AlterField(
            model_name='harvestallocation',
            name='allocated_volume',
            field=models.DecimalField(decimal_places=2, help_text='Volume of juice allocated in liters', max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='harvestallocation',
            name='created_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='harvest_allocation_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='harvestallocation',
            name='harvest',
            field=models.ForeignKey(help_text='Harvest being allocated', on_delete=django.db.models.deletion.PROTECT, related_name='harvest_allocations', to='harvests.harvest'),
        ),
        migrations.AlterField(
            model_name='harvestallocation',
            name='tank',
            field=models.ForeignKey(help_text='Tank receiving the juice', on_delete=django.db.models.deletion.PROTECT, related_name='harvest_allocations', to='cellars.tank'),
        ),
    ]
