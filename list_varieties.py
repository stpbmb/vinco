from vineyards.models import GrapeVariety

print("\n=== Red Varieties ===")
for v in GrapeVariety.objects.filter(type='red').order_by('code'):
    print(f"{v.code}: {v.name} ({v.system_code})")

print("\n=== White Varieties ===")
for v in GrapeVariety.objects.filter(type='white').order_by('code'):
    print(f"{v.code}: {v.name} ({v.system_code})")

print("\n=== Organization Info ===")
for v in GrapeVariety.objects.all():
    print(f"Variety: {v.name}, Organization: {v.organization_id}")
