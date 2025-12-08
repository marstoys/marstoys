from django.contrib import admin
from .models import CustomUser,UserOtp
from django.utils.html import format_html

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser


    list_display = ("first_name", "last_name", "tg_id","phone_number",  "order_map_link")


    fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "role","phone_number","tg_id",  "address","lat","lang")}),
    )

    add_fieldsets = (
        (None, {"fields": ( "first_name", "last_name", "role","phone_number","tg_id",   "address","lat","lang")}),
    )
    def order_map_link(self, obj):
        user = obj

        if not user:
            return "❌ Mavjud emas"

        if getattr(user, "lat", None) and getattr(user, "lang", None):
            lat = user.lat
            lon = user.lang
            url = f"https://www.google.com/maps?q={lat},{lon}"

            return format_html(
                '<a href="{}" target="_blank" style="font-weight:600;">📍 Xaritada (GPS)</a>',
                url
            )

        # 2️⃣ Agar koordinata bo‘lmasa — address matni bo‘yicha ochiladi
        if user.address:
            address = user.address.replace(" ", "+")
            url = f"https://www.google.com/maps?q={address}"

            return format_html(
                '<a href="{}" target="_blank" style="font-weight:600;">📍 Xaritada (Manzil)</a>',
                url
            )

    # 3️⃣ Umuman maʼlumot bo‘lmasa
        return "❌ Maʼlumot yo‘q"

    order_map_link.short_description = "Manzil (Google Maps)"


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserOtp)