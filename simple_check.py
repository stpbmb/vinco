from vineyards.models import GrapeVariety

print("=== Grape Varieties Count ===")
print(f"Total varieties: {GrapeVariety.objects.count()}")
