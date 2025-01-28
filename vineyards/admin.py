from django.contrib import admin
from .models import (
    Company,
    Supplier,
    Vineyard,
    Harvest,
    Cellar,
    Tank,
    CrushedJuiceAllocation
)

# Register all models in one place
admin.site.register(Company)
admin.site.register(Supplier)
admin.site.register(Vineyard)
admin.site.register(Harvest)
admin.site.register(Cellar)
admin.site.register(Tank)
admin.site.register(CrushedJuiceAllocation)
