from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import *
from accounts.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import Group
admin.site.unregister(Group)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form, change_form = UserCreationForm, UserChangeForm
    list_display = ('phone', 'username', 'email', 'is_active', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        ('Authentication', {'fields': ('phone', 'username', 'email', 'password')}),
        ('personal info', {'fields': ('firstname', 'lastname', 'image')}),
        ('permission', {'fields': ('is_active', 'is_admin', 'is_superuser')})
    )
    add_fieldsets = (
        None, dict({
            'class': ('wide',),
            'fields': ('phone', 'password1', 'password2')
        })
    )
    search_fields = 'phone',
    ordering = 'phone',
    filter_horizontal = []