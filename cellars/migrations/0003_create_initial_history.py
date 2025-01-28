from django.db import migrations
from django.utils import timezone

def create_initial_history(apps, schema_editor):
    Tank = apps.get_model('cellars', 'Tank')
    TankHistory = apps.get_model('cellars', 'TankHistory')
    User = apps.get_model('auth', 'User')
    
    # Get the first superuser as the creator
    creator = User.objects.filter(is_superuser=True).first()
    if not creator:
        return
        
    for tank in Tank.objects.all():
        if tank.current_volume > 0 and not TankHistory.objects.filter(tank=tank).exists():
            # Create an initial allocation entry
            TankHistory.objects.create(
                tank=tank,
                operation_type='allocation',
                date=timezone.now().date(),
                volume=tank.current_volume,
                notes='Initial tank volume',
                created_by=creator
            )

def reverse_initial_history(apps, schema_editor):
    TankHistory = apps.get_model('cellars', 'TankHistory')
    TankHistory.objects.filter(notes='Initial tank volume').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('cellars', '0002_alter_crushedjuiceallocation_harvest_and_more'),  # Update this to your previous migration
    ]

    operations = [
        migrations.RunPython(create_initial_history, reverse_initial_history),
    ]
