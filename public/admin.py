from django.contrib import admin
from public.models import Deal, PropertyOutlook, PropertyType, PropertyArea, Governorate

# Register your models here.

admin.site.register(Deal)
admin.site.register(PropertyType)
admin.site.register(PropertyArea)
admin.site.register(PropertyOutlook)
admin.site.register(Governorate)