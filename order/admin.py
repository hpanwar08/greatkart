from django.contrib import admin

# Register your models here.
from order.models import Order, Payment, OrderItem

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(OrderItem)