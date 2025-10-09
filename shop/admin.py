from django.urls import path
from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.template.response import TemplateResponse
class ImageProductsInline(admin.TabularInline):
    model = ImageProducts
    extra = 1


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount", "colored_price", "product_image")
    list_filter = ("category",)
    search_fields = ("name",)
    inlines = [ImageProductsInline]
    readonly_fields = ("product_image",)

    def colored_price(self, obj):
        return format_html(
            '<span style="color:{};">{} so’m</span>',
            "green" if obj.discount > 0 else "black",
            obj.discounted_price if hasattr(obj, "discounted_price") else obj.price,
        )
    colored_price.short_description = "Chegirmali narx"

    def product_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;" />',
                               first_image.image.url)
        return "—"
    product_image.short_description = "Rasm"





class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "product_image", "calculated_total_price")

    def calculated_total_price(self, obj):
        return f"{obj.quantity * obj.product.discounted_price:,} so’m"
    calculated_total_price.short_description = "Jami narx"

    def product_image(self, obj):
        img = obj.product.images.first()
        if img:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:8px;" />', img.image.url)
        return "—"
    product_image.short_description = "Rasm"


class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "ordered_by_name", "payment_method", "is_paid", "status", "created_datetime")
    list_filter = ("status", "is_paid", "payment_method")
    search_fields = ("ordered_by__first_name", "order_number")
    readonly_fields = ("ordered_by", "payment_method", "is_paid", "order_number", "created_datetime", "modified_datetime")
    inlines = [OrderItemInline]

    def ordered_by_name(self, obj):
        return obj.ordered_by.first_name if obj.ordered_by else "No User"
    ordered_by_name.short_description = "Buyurtmachi"




class CustomHTMLAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.custom_view), name='admin-custom-html'),
        ]
        return custom_urls + urls

    def custom_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            title="📄 Excel eksport sahifasi",
        )
        return TemplateResponse(request, "shop/index.html", context)

    
class DummyModel(models.Model):
    class Meta:
        verbose_name_plural = "📄 Oyinchoq exel yuklash"
        managed = False
        



admin.site.register(DummyModel, CustomHTMLAdmin)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Order, OrderAdmin)

