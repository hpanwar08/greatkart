from django.contrib import admin

from order.models import Payment, OrderItem, Order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['payment', 'product', 'user', 'quantity', 'product_price', 'ordered', 'created_at']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'get_full_name', 'phone', 'email', 'city', 'payment', 'tax', 'order_total',
                    'is_ordered', 'status', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'payment', 'product', 'user', 'quantity', 'product_price', 'ordered', 'created_at']
