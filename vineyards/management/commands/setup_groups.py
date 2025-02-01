from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from vineyards.models import Vineyard, Supplier

class Command(BaseCommand):
    help = 'Create default user groups and permissions'

    def handle(self, *args, **options):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Administrators')
        manager_group, _ = Group.objects.get_or_create(name='Managers')
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        viewer_group, _ = Group.objects.get_or_create(name='Viewers')

        # Get content types
        vineyard_ct = ContentType.objects.get_for_model(Vineyard)
        supplier_ct = ContentType.objects.get_for_model(Supplier)

        # Get all permissions
        vineyard_perms = Permission.objects.filter(content_type=vineyard_ct)
        supplier_perms = Permission.objects.filter(content_type=supplier_ct)

        # Assign permissions to groups
        # Administrators get all permissions
        admin_group.permissions.add(*vineyard_perms, *supplier_perms)

        # Managers get most permissions except some administrative ones
        manager_perms = Permission.objects.filter(
            content_type__in=[vineyard_ct, supplier_ct]
        ).exclude(codename__in=['delete_vineyard', 'delete_supplier'])
        manager_group.permissions.add(*manager_perms)

        # Staff get view and basic management permissions
        staff_perms = Permission.objects.filter(
            content_type__in=[vineyard_ct, supplier_ct],
            codename__in=[
                'view_vineyard', 'add_vineyard', 'change_vineyard',
                'view_supplier', 'add_supplier', 'change_supplier',
                'view_vineyard_analytics', 'view_supplier_analytics'
            ]
        )
        staff_group.permissions.add(*staff_perms)

        # Viewers only get view permissions
        viewer_perms = Permission.objects.filter(
            content_type__in=[vineyard_ct, supplier_ct],
            codename__in=['view_vineyard', 'view_supplier']
        )
        viewer_group.permissions.add(*viewer_perms)

        self.stdout.write(self.style.SUCCESS('Successfully set up groups and permissions'))
