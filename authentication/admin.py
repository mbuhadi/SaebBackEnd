from django.contrib import admin
from .models import UserAccount, TemporaryToken

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(TemporaryToken)
