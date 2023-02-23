from django.db import models

class Office(models.Model):
    name_en = models.CharField(max_length=60)
    name_ar = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="offices/")
    owner = models.OneToOneField(
        "dealer.Dealer",
        blank=True,
        null=True,
        unique=True,
        related_name="office_owner",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name_ar
