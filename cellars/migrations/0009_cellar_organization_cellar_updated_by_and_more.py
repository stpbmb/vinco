# Generated by Django 5.1.5 on 2025-02-03 19:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cellars', '0008_remove_cellar_capacity_field'),
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cellar',
            name='organization',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='organizations.organization'),
        ),
        migrations.AddField(
            model_name='cellar',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tank',
            name='organization',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='organizations.organization'),
        ),
        migrations.AddField(
            model_name='tank',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tankhistory',
            name='organization',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='organizations.organization'),
        ),
        migrations.AddField(
            model_name='tankhistory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='tankhistory',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]
