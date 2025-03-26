from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser


    list_display = ("first_name", "last_name", "phone_number", "address")


    fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "phone_number",  "address")}),
    )

    add_fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "phone_number",  "address")}),
    )

    # Hide default fields from admin
    exclude = ('username',"is_staff", "is_superuser", "groups", "user_permissions", "date_joined", "email")

admin.site.register(CustomUser, CustomUserAdmin)
