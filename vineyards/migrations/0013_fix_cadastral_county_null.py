from django.db import migrations, models

def forwards_func(apps, schema_editor):
    # Get the historical version of the model
    Vineyard = apps.get_model("vineyards", "Vineyard")
    # Update all NULL values to empty string
    Vineyard.objects.filter(cadastral_county__isnull=True).update(cadastral_county='')

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('vineyards', '0012_alter_vineyard_cadastral_county'),
    ]

    operations = [
        # First, convert NULL to empty string
        migrations.RunPython(forwards_func, reverse_func),
        
        # Then modify the field to allow NULL
        migrations.AlterField(
            model_name='vineyard',
            name='cadastral_county',
            field=models.CharField(
                blank=True,
                null=True,
                max_length=100,
                help_text="Cadastral county where the vineyard is located"
            ),
        ),
    ]
