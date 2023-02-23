from django.contrib import admin

from .models import (
    AdminUser,
    Role,
    Purchase,
    Offer,
    CarryOver,
    Transaction,
    Message,
    Credit,
    Log,
)

admin.site.register(AdminUser)
admin.site.register(Role)
admin.site.register(Purchase)
admin.site.register(Offer)
admin.site.register(CarryOver)
admin.site.register(Transaction)
admin.site.register(Message)
admin.site.register(Credit)
admin.site.register(Log)
