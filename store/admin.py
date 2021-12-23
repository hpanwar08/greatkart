from django.contrib import admin

from store.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'slug', 'price', 'stock', 'category', 'modified_at', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
