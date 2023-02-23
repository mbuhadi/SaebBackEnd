from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from administration.models import CarryOver
from utility import get_last_month_indexed_date, get_today_indexed_date
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from public.models import Deal
import datetime
from dealer.models import Dealer
from administration.models import DeletedDeal, DealLog

MAX_CARRY_OVER = 15


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        every_day,
        id="every_day",
        trigger=CronTrigger(day="*/1"),
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()


def every_day(custom_date=None):
    date_thirty_days_ago = datetime.datetime.today() - datetime.timedelta(days=30)
    if custom_date:
        date_thirty_days_ago = custom_date
    Deal.objects.filter(date_created__lt=date_thirty_days_ago).delete()
    if datetime.date.today().day != 1:
        return
    # By the end of the month, calculate CarryOver
    last_month = get_last_month_indexed_date()
    today = get_today_indexed_date()
    carry_overs = []
    for dealer in Dealer.objects.all():
        if dealer.remaining <= 0:
            continue

        remaining = dealer.get_remaining_by_date(last_month)
        remaining = min(remaining, MAX_CARRY_OVER)
        carry_overs.append(
            CarryOver(
                dealer=dealer,
                amount=remaining,
                indexed_date=today,
            )
        )
    CarryOver.objects.bulk_create(carry_overs)
    # if deals:
    #     for deal in deals:
    #         deal.delete()
