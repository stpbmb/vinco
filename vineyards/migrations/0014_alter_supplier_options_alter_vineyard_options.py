# Generated by Django 5.1.5 on 2025-02-01 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vineyards', '0013_fix_cadastral_county_null'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='supplier',
            options={'ordering': ['name'], 'permissions': [('view_all_suppliers', 'Can view all suppliers'), ('manage_suppliers', 'Can manage suppliers'), ('export_supplier_data', 'Can export supplier data'), ('view_supplier_analytics', 'Can view supplier analytics')]},
        ),
        migrations.AlterModelOptions(
            name='vineyard',
            options={'ordering': ['name'], 'permissions': [('view_all_vineyards', 'Can view all vineyards'), ('manage_vineyards', 'Can manage vineyards'), ('export_vineyard_data', 'Can export vineyard data'), ('view_vineyard_analytics', 'Can view vineyard analytics')], 'verbose_name': 'Vineyard', 'verbose_name_plural': 'Vineyards'},
        ),
    ]
