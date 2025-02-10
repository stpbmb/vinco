from django.db import connection
from vineyards.models import GrapeVariety, Vineyard

def check_structure():
    print("\n=== Table Structure ===")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'vineyards_grapevariety'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))

def check_data():
    print("\n=== Grape Varieties Data ===")
    print("\nRed Varieties:")
    for variety in GrapeVariety.objects.filter(type='red').order_by('code'):
        print(f"{variety.code}: {variety.name} (system: {variety.system_code})")
    
    print("\nWhite Varieties:")
    for variety in GrapeVariety.objects.filter(type='white').order_by('code'):
        print(f"{variety.code}: {variety.name} (system: {variety.system_code})")

def check_vineyard_properties():
    print("\n=== Testing Vineyard Properties ===")
    vineyard = Vineyard.objects.first()
    if vineyard:
        print(f"Vineyard: {vineyard.name}")
        print(f"Grape Variety: {vineyard.grape_variety}")
        print(f"Variety Code: {vineyard.variety_code}")
        print(f"Variety Type: {vineyard.variety_type}")

if __name__ == "__main__":
    check_structure()
    check_data()
    check_vineyard_properties()
