from django.contrib import admin
from dealer.models import Dealer
from administration.models import DeletedDeal, DealLog

# Register your models here.
admin.site.register(Dealer)
admin.site.register(DealLog)
admin.site.register(DeletedDeal)
