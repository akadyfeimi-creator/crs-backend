import re
from django.core.exceptions import ValidationError


class ComplexityValidator:
    """
    Enforces password complexity: at least one uppercase letter, one
    lowercase letter, one digit, and one special character. Implements
    the credential strength control expected under OWASP MASVS-AUTH
    and CBN's authentication requirements.
    """

    def validate(self, password, user=None):
        errors = []
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
            errors.append("Password must contain at least one special character.")
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, one "
            "lowercase letter, one digit, and one special character."
        )