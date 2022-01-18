from django.db import models
from store.models import Product

# Create your models here.
from django.utils import timezone


class Cart(models.Model):
    cart_id = models.CharField(max_length=256, blank=True)
    date_added = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.product_name}"
