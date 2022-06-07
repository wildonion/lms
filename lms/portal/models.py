




from django.db import models
from django.utils import timezone


class PaymentInfo(models.Model):
    user_id = models.IntegerField(default=0)
    product_id  = models.IntegerField(default=0)
    authority = models.TextField(default='')
    verification_code = models.TextField(default='')
    ref_id = models.TextField(default='')
    card_pan = models.TextField(default='')
    card_hash = models.TextField(default='')
    fee_type = models.TextField(default='')
    fee = models.IntegerField(default=0)
    requested_at = models.DateTimeField(default=timezone.now())
    paid_at = models.DateTimeField(null=True, blank=True)