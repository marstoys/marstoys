from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    class Meta:
        verbose_name = "Do'kon"
        verbose_name_plural = "Do'konlar"