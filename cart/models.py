from django.db import models
# Create your models here.
from django.utils import timezone

from accounts.models import Account
from store.models import Product, Variation


class Cart(models.Model):
    cart_id = models.CharField(max_length=256, blank=True)
    date_added = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    buyer = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items', null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.product_name}"
