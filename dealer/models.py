from django.db import models
from django.db.models import Sum
from utility import get_today_indexed_date
import datetime

# from public.models import Deal


class Dealer(models.Model):
    phone = models.CharField(
        max_length=8,
        primary_key=True,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=60)
    office = models.ForeignKey(
        "office.Office", on_delete=models.CASCADE, related_name="dealers"
    )

    @property
    def post_count(self):
        return self.logs.filter(indexed_date=get_today_indexed_date()).count()

    @property
    def credit(self):
        credit = self.credits.filter(indexed_date=get_today_indexed_date())
        if credit.exists():
            return credit.aggregate(limit=Sum("amount"))["limit"]
        else:
            return 0

    @property
    def get_carry_over(self):
        carry = self.carry_over.filter(indexed_date=get_today_indexed_date())
        if carry.exists():
            return carry.first().amount
        else:
            return 0

    @property
    def remaining(self):
        return (self.credit + self.get_carry_over) - self.post_count

    def get_remaining_by_date(self, indexed_date):
        deleted = self.deleted_deals.filter(logs__indexed_date=indexed_date).count()
        deals = self.deals.filter(logs__indexed_date=indexed_date).count()
        count = deleted + deals
        limit = 0
        # purchases queries by index date + if the purchase instance HAS a transaction instance
        credits = self.credits.filter(indexed_date=indexed_date)
        if credits.exists():
            limit = credits.aggregate(limit=Sum("credit"))["limit"]

        if self.carry_over.filter(indexed_date=indexed_date).exists():
            # pylint: disable= no-member
            limit += self.carry_over.first().amount

        return limit - count

    def __str__(self):
        return self.phone


# alt code for get cary over
# end_of_today = datetime.datetime.today().replace(hour=23, minute=59, second=0, microsecond=0)
# carry = self.carry_over.filter(date__lte=datetime.datetime.today(), date__gt=end_of_today-datetime.timedelta(days=31))

# alt code for post_count
# end_of_today = datetime.datetime.today().replace(hour=23, minute=59, second=0, microsecond=0)
# return self.logs.filter(date__lte=datetime.datetime.today(), date__gt=end_of_today-datetime.timedelta(days=31)).count()

# alt code for credit
# end_of_today = datetime.datetime.today().replace(hour=23, minute=59, second=0, microsecond=0)
# purchases gives us all instances that occured after 23:59 31 days ago.
# purchases = self.purchases.filter(date_fullfilled__lte=datetime.datetime.today(), date_fullfilled__gt=end_of_today-datetime.timedelta(days=31))