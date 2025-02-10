from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DELETE FROM django_migrations WHERE app='vineyards' AND name IN ('0017_grapevariety', '0018_load_initial_grape_varieties');")
