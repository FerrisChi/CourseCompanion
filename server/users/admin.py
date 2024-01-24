from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser

class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address', 'profile_picture')}),
    )
    # layout of the admin add form, which is used when creating new instances
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'address', 'profile_picture')
        }),
    )

admin.site.register(MyUser, MyUserAdmin)

