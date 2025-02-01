from django.core.management.base import BaseCommand
from django.db.models import Sum
from cellars.models import Tank
from harvests.models import HarvestAllocation

class Command(BaseCommand):
    help = 'Check and optionally fix tank volumes based on their allocations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix incorrect tank volumes',
        )

    def handle(self, *args, **options):
        fix_volumes = options['fix']
        tanks = Tank.objects.all()
        
        for tank in tanks:
            # Calculate total allocated volume
            allocated_volume = HarvestAllocation.objects.filter(
                tank=tank
            ).aggregate(
                total=Sum('allocated_volume')
            )['total'] or 0
            
            allocated_volume = float(allocated_volume)
            current_volume = float(tank.current_volume)
            
            if abs(allocated_volume - current_volume) > 0.01:  # Allow small float differences
                self.stdout.write(
                    self.style.WARNING(
                        f'Tank {tank.name}: Current volume ({current_volume}L) '
                        f'differs from allocations ({allocated_volume}L)'
                    )
                )
                
                if fix_volumes:
                    tank.current_volume = allocated_volume
                    tank.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Fixed tank {tank.name}: Set volume to {allocated_volume}L'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Tank {tank.name}: Volume correct ({current_volume}L)'
                    )
                )
