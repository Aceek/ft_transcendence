from django.db import models
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from uuid import uuid4


class TwoFactorEmailModel(models.Model):
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(default=now() + timedelta(minutes=10))
    user = models.ForeignKey(to='CustomUser.CustomUser', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_random_string(length=6, allowed_chars="0123456789")
        if not self.pk and not self.expiration:
            self.expiration = now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def send_two_factor_email(self):
        subject = "ft-transcendence.fr | Your 2FA Code"
        body = f"Your 2FA code is: {self.code}"
        send_mail(subject, body, None, [self.user.email])

    def can_be_sent(self, code):
        return self.expiration > now() and self.code == code

    def is_expired(self):
        return self.expiration < now()

    def gen_code(self):
        self.code = get_random_string(length=6, allowed_chars="0123456789")
        self.save()
