from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'first_name')  # to make fields as links
    readonly_fields = ('last_login', 'date_joined')

    list_filter = ()
    fieldsets = ()
