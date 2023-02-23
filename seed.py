# pylint: skip-file
# flake8: noqa
from authentication.models import UserAccount
from public.models import PropertyType, PropertyArea, Deal, PropertyOutlook
from dealer.models import Dealer
from office.models import Office
from authentication.models import UserAccount
from administration.models import Role, AdminUser, Offer, Purchase
from utility import get_today_indexed_date, create_reference_id
import datetime

# Delete all models
Deal.objects.all().delete()
Dealer.objects.all().delete()
Office.objects.all().delete()
PropertyType.objects.all().delete()
PropertyArea.objects.all().delete()
PropertyOutlook.objects.all().delete()
Offer.objects.all().delete()
UserAccount.objects.all().delete()

# "seed/super_admin.png"
# "seed/chainedram_office.png"

test_img = "http://s3.amazonaws.com/saebalaqar/Business.jpg"

try:
    UserAccount.objects.create_superuser(
        phone="admin", password="admin", image="seed/super_admin.png"
    )
except:
    print("Failed to create supoer admin")


house, _ = PropertyType.objects.get_or_create(name_ar="House", name_en="House")
land, _ = PropertyType.objects.get_or_create(name_ar="Land", name_en="Land")

shuhada, _ = PropertyArea.objects.get_or_create(name_ar="Shuhada", name_en="Shuhada")
bayan, _ = PropertyArea.objects.get_or_create(name_ar="Bayan", name_en="Bayan")

TwoStreets, _ = PropertyOutlook.objects.get_or_create(
    name_ar="TwoStreets", name_en="TwoStreets"
)
ThreeStreets, _ = PropertyOutlook.objects.get_or_create(
    name_ar="ThreeStreets", name_en="ThreeStreets"
)

chainedRamOffice, _ = Office.objects.get_or_create(
    name_ar="ChainedRam", name_en="ChainedRam", image="seed/chainedram_office.png"
)

rambotDealer, _ = Dealer.objects.get_or_create(
    phone="12345678", name="Rambot", office=chainedRamOffice
)
webDealer, _ = Dealer.objects.get_or_create(
    phone="11223344", name="Rambot", office=chainedRamOffice
)
chainedRamOffice.owner = rambotDealer
chainedRamOffice.save()


Deal.objects.get_or_create(
    property_area=shuhada,
    property_type=house,
    property_outlook=TwoStreets,
    dealer=rambotDealer,
    description="Some description",
)
superAdminRole, _ = Role.objects.get_or_create(name="super admin", permissions=0)
AdminUser.objects.get_or_create(dealer=rambotDealer, role=superAdminRole, is_admin=True)
AdminUser.objects.get_or_create(dealer=webDealer, role=superAdminRole, is_admin=True)

offer, _ = Offer.objects.get_or_create(
    name_ar="10 deals per month",
    name_en="10 deals per month",
    price=5,
    image="seed/chainedram_office.png",
    credit=10,
    duration=5
)

Purchase.objects.get_or_create(
    dealer=rambotDealer, credit=10, indexed_date=get_today_indexed_date()
)

Purchase.objects.get_or_create(
    dealer=webDealer, credit=10, indexed_date=get_today_indexed_date()
)

# Status.objects.get_or_create(name="Complete")
# Status.objects.get_or_create(name="Pending")
# Status.objects.get_or_create(name="Cancelled")
# Status.objects.get_or_create(name="Expired")

# Method.objects.get_or_create(name="KNET")
# Method.objects.get_or_create(name="Direct")

print("Done!")
