from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from accounts.models import Account, UserProfile


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'first_name')  # to make fields as links
    readonly_fields = ('last_login', 'date_joined')

    list_filter = ()
    fieldsets = ()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')