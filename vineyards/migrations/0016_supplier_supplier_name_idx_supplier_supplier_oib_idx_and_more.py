# Generated by Django 5.1.5 on 2025-02-04 19:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('vineyards', '0015_supplier_organization_supplier_updated_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['name'], name='supplier_name_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['oib'], name='supplier_oib_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['created_at'], name='supplier_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['name'], name='vineyard_name_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['location'], name='vineyard_location_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['grape_variety'], name='vineyard_grape_var_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['ownership_type'], name='vineyard_ownership_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['size'], name='vineyard_size_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['created_at'], name='vineyard_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='vineyard',
            index=models.Index(fields=['supplier', 'ownership_type'], name='vineyard_sup_own_idx'),
        ),
    ]
