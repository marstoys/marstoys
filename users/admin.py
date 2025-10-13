from django.contrib import admin
from .models import CustomUser,UserOtp

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser


    list_display = ("first_name", "last_name", "phone_number", "address")


    fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "phone_number",  "address")}),
    )

    add_fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "phone_number",  "address")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserOtp)