# from django.db.models.signals import post_save, pre_delete
# from django.dispatch import receiver
# from django.shortcuts import get_object_or_404
# from utility import get_today_indexed_date
# from dealer.models import Dealer
# from administration.models import Purchase


# @receiver(post_save, sender=Purchase)
# def update_postlimit(sender, instance: Purchase, **kwargs):
#     dealer_ = get_object_or_404(Dealer,phone = instance.dealer.phone)
#     dealer_.credit = dealer_.credit + instance.offer.credit
#     dealer_.save()