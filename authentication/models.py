from administration.models import AdminUser
import re
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from public.models import Dealer
from office.models import Office


class UserAccountManager(BaseUserManager):
    def create_user(
        self, phone, dealer, password=None, email=None, name=None, is_super=False
    ):
        if not phone:
            raise ValueError("Users must have an phone number")

        if is_super:
            user = self.model(phone=phone, name=name, password=password)
            user.set_password(password)
            user.save()
            return user

        email = self.normalize_email(email)
        if not re.match(r"\d{8}", phone):
            raise ValueError("phone must be 8 digits long")
        user = self.model(phone=phone, name=name, email=email, dealer=dealer)

        return user

    def create_superuser(self, phone, password, image="seed/chainedram_office.png"):
        (office, _) = Office.objects.get_or_create(
            name_en="administration",
            name_ar="administration",
        )
        office.image = image
        office.save()
        dealer = Dealer(name="Admin", phone=phone, office=office)
        dealer.save()
        office.owner = dealer
        office.save()
        user = self.create_user(
            phone=phone,
            password=password,
            dealer=dealer,
            name="Admin",
            is_super=True,
        )

        AdminUser.objects.create(dealer=dealer, is_admin=True)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """DataBase model for users"""

    phone = models.CharField(max_length=8, unique=True)
    dealer = models.OneToOneField(
        Dealer,
        to_field="phone",
        null=True,
        unique=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    name = models.CharField(
        max_length=255,
        null=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = "phone"

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = None
        super(UserAccount, self).save(*args, **kwargs)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.phone


class TemporaryToken(models.Model):
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return self.dealer.phone + ": " + self.otp
