from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from organizations.models import Organization, OrganizationUser

User = get_user_model()

class Command(BaseCommand):
    help = 'Assigns an organization to a user'

    def handle(self, *args, **options):
        # Get the user first since we need it for created_by
        try:
            user = User.objects.get(username='stpbmb')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User stpbmb not found'))
            return

        # Get or create the organization
        org_name = 'Vinarija Kaptol'
        org, created = Organization.objects.get_or_create(
            name=org_name,
            defaults={
                'slug': slugify(org_name),
                'address': 'Kaptol, Croatia',
                'tax_number': 'HR12345678901',  # Example tax number
                'contact_email': 'contact@vinarija-kaptol.hr',
                'contact_phone': '+385 1 234 5678',
                'created_by': user,
                'updated_by': user,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing organization: {org.name}'))

        # Create organization user relationship if it doesn't exist
        org_user, created = OrganizationUser.objects.get_or_create(
            user=user,
            organization=org,
            defaults={
                'role': 'owner',  # Make them an owner by default
                'is_primary': True,
                'created_by': user,
                'updated_by': user,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Added user {user.username} to organization {org.name} as owner')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'User {user.username} is already a member of {org.name}')
            )
