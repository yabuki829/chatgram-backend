from django.contrib import admin

# Register your models here.
from .models import Broadcast,Location,TVStation,Program


admin.site.register(Broadcast)
admin.site.register(Location)
admin.site.register(TVStation)
admin.site.register(Program)