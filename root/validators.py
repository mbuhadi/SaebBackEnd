from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_min_text(val):
    if len(val) < 100:
        raise ValidationError(
            _('Ensure this field has no less than 100 characters.'),
            params={'value': val},
        )
