from django.core.exceptions import ValidationError
import re


def validate_password(password):
    """Validate that a password meets certain requirements."""
    if len(password) < 8:
        raise ValidationError(
            'Password must be at least 8 characters long.'
        )
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            'Password must contain at least one uppercase letter.'
        )
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            'Password must contain at least one lowercase letter.'
        )
    if not re.search(r'\d', password):
        raise ValidationError(
            'Password must contain at least one digit.'
        )
    if re.search(r'(?i)([\w])\1+', password):
        raise ValidationError(
            'Password cannot contain sequential characters.'
        )
    if not re.search(r'[^\w\s]', password):
        raise ValidationError(
            'Password must contain at least one special character.'
        )