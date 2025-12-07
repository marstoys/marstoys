from django.contrib import admin
from .models import CustomUser,UserOtp

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser


    list_display = ("first_name", "last_name", "tg_id","phone_number", "address",)


    fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "role","phone_number","tg_id",  "address","lat","lang")}),
    )

    add_fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "role","phone_number","tg_id",   "address","lat","lang")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserOtp)