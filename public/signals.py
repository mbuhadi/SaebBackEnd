from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from utility import get_today_indexed_date
from public.models import Deal
from administration.models import DealLog, DeletedDeal


@receiver(post_save, sender=Deal)
def log_deal_date(sender, instance: Deal, **kwargs):
    DealLog(
        deal=instance, dealer=instance.dealer, indexed_date=get_today_indexed_date()
    ).save()


@receiver(pre_delete, sender=Deal)
def on_deal_delete(sender, instance: Deal, **kwargs):
    deleted_deal = DeletedDeal.objects.create(
        id=instance.id,
        dealer=instance.dealer,
        property_type=instance.property_type,
        property_area=instance.property_area,
        property_outlook=instance.property_outlook,
        description=instance.description,
    )
    DealLog.objects.filter(deal=instance.id).update(deleted_deal=deleted_deal.id)