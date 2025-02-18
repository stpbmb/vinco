# Generated by Django 5.1.5 on 2025-02-10 20:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('vineyards', '0016_supplier_supplier_name_idx_supplier_supplier_oib_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GrapeVariety',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(help_text="Official variety code (e.g., 'CV036')", max_length=5)),
                ('name', models.CharField(help_text='Official variety name', max_length=100)),
                ('type', models.CharField(choices=[('red', 'Red'), ('white', 'White')], help_text='Type of grape variety', max_length=10)),
                ('system_code', models.CharField(help_text="Internal system code (e.g., 'cabernet_sauvignon')", max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grape_varieties_created', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='organizations.organization')),
                ('updated_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'grape variety',
                'verbose_name_plural': 'grape varieties',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['code'], name='variety_code_idx'), models.Index(fields=['system_code'], name='variety_system_code_idx'), models.Index(fields=['type'], name='variety_type_idx')],
                'constraints': [models.UniqueConstraint(fields=('organization', 'code'), name='unique_variety_code_per_org')],
            },
        ),
    ]
