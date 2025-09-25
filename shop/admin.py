from django.urls import path
from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.http import HttpResponse, HttpResponseForbidden
admin.site.site_header = 'E-Commerce Admin'
from django.template.response import TemplateResponse
class ImageProductsInline(admin.TabularInline):
    model = ImageProducts
    extra = 1


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "discount", "quantity", "category", "product_image")
    inlines = [ImageProductsInline]

    def product_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                               first_image.image.url)
        return "No Image"

    product_image.short_description = "Rasm:"




class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    exclude = ('total_price',)
    readonly_fields = ('product', 'quantity', 'calculated_total_price', "product_image",)


    def calculated_total_price(self, obj):
        return obj.quantity * obj.product.discounted_price

    calculated_total_price.short_description = "Jami narxi:"

    def product_image(self, obj):
        if obj and obj.product and obj.product.images.exists():
            first_image = obj.product.images.first()
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                               first_image.image.url)
        return "No Image"

    product_image.short_description = "O'yinchoq rasmi:"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
         "ordered_by_name",  "payment_method", "is_paid", "status")
    list_filter = ("is_paid", "payment_method")
    search_fields = ("ordered_by__first_name", "ordered_by__username")
    inlines = [OrderItemInline]
    
    readonly_fields = (
        "ordered_by","payment_method", "is_paid","order_number",  "created_datetime", "modified_datetime", "payment_link")

    def ordered_by_name(self, obj):
        return obj.ordered_by.first_name if obj.ordered_by else "No User"

    ordered_by_name.short_description = "Ordered By"



class CustomHTMLAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.custom_view), name='admin-custom-html'),
        ]
        return custom_urls + urls

    def custom_view(self, request):
      
       
        return TemplateResponse(request, "shop/index.html",)
    
class DummyModel(models.Model):
    class Meta:
        verbose_name_plural = "📄 Oyinchoq exel yuklash"
        managed = False
        



admin.site.register(DummyModel, CustomHTMLAdmin)
admin.site.register(Category)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Order, OrderAdmin)

