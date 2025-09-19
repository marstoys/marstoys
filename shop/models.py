import cloudinary.uploader
from decimal import Decimal
from django.db.models import Avg, Sum
from users.models import CustomUser as User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete
from cloudinary.models import CloudinaryField
from core.models.basemodel import SafeBaseModel
from core.constants import COLOR_CHOICES
# Create your models here.



class Category(SafeBaseModel):
    GENDER_CHOICES = [
        ('male', "O'g'il bolalar uchun"),
        ('female', 'Qiz bolalar uchun'),
        ('all',"Barcha uchun")
    ]
    gender=models.CharField(choices=GENDER_CHOICES, max_length=6,default='male', verbose_name='Kimlar uchun:')
    name:str = models.CharField(max_length=100,default='ok',verbose_name='Kategory nomi (uzb)')
    name_ru = models.CharField(max_length=100,default='ok',verbose_name='Kategory nomi (rus)')
    name_en = models.CharField(max_length=100,default='ok',verbose_name='Kategory nomi (eng)')

    @property
    def product_count(self):
        return self.products.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

class Colors(SafeBaseModel):
    name=models.CharField(choices=COLOR_CHOICES, max_length=50, unique=True)
    def __str__(self):
        
        return dict(COLOR_CHOICES).get(self.name, self.name)
    class Meta:
        verbose_name = "Rang"
        verbose_name_plural = "Ranglar"
class Products(SafeBaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya:",related_name="products")
    name = models.CharField(max_length=100,default='ok', verbose_name="O'yinchoq nomi (uzb):")
    name_ru = models.CharField(max_length=100,default='ok', verbose_name="O'yinchoq nomi (rus):")
    name_en = models.CharField(max_length=100,default='ok', verbose_name="O'yinchoq nomi (eng):")
    price = models.DecimalField(decimal_places=2, max_digits=14, verbose_name="O'yinchoq narxi (Faqat so'mda):")
    color = models.ManyToManyField(Colors, blank=True, verbose_name="O'yinchoq rangi:")
    discount = models.IntegerField(default=0, verbose_name="O'yinchoq chegirmasi: (ixtiyoriy)")
    description = models.TextField(null=True, blank=True, verbose_name="O'yinchoq xaqida (uzb):")
    description_ru = models.TextField(null=True, blank=True, verbose_name="O'yinchoq xaqida (rus):")
    description_en = models.TextField(null=True, blank=True, verbose_name="O'yinchoq xaqida (eng):")
    quantity = models.IntegerField(verbose_name="O'yinchoq soni:")
    sku=models.CharField(max_length=100,blank=True, verbose_name="O'yinchoq karobkasidagi kod:")
    video_url = models.URLField(null=True, blank=True, verbose_name="You tubdan video joylash:")




    @property
    def discounted_price(self):
        if self.discount > 0:
            discounted = self.price * Decimal(1 - self.discount / 100)
            return Decimal(f'{discounted}').quantize(Decimal('0.00'))
        return Decimal(f'{self.price}').quantize(Decimal('0.00'))
    @property
    def average_rating(self):
        avg_rating = self.comments.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    @property
    def sold(self):
        return self.ordered_products.aggregate(Sum("quantity"))[
            "quantity__sum"] or 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"


class ImageProducts(SafeBaseModel):
    product = models.ForeignKey(Products, related_name="images", on_delete=models.CASCADE)
    image = CloudinaryField("image")

    class Meta:
        verbose_name = "Rasm"
        verbose_name_plural = "Rasmlar"


@receiver(post_delete, sender=ImageProducts)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        try:
            cloudinary.uploader.destroy(instance.image.public_id)
        except Exception as e:
            print(f"Cloudinary rasm o‘chirishda xatolik: {e}")


class Order(SafeBaseModel):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('delivering','Yetkazilmoqda'),
        ('delivered', 'Yetkazib berildi'),
        ('cancelled', 'Bekor qilindi'),

    ]
    PAYMENT_METHOD_CHOICES = [
        ('naxt', 'Naxt'),
        ('karta', 'Karta'),
    ]
    ordered_by = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=6, default='naxt',
                                      verbose_name='Tolov turi:')
    payment_link = models.URLField(blank=True, null=True, verbose_name='Tolov qilish uchun link:')
    is_paid = models.BooleanField(default=False, verbose_name='Tolanganligi:')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Buyurtma xolati:')
    

    def __str__(self):
        return f"Ordered by {self.ordered_by.full_name} - Status: {self.status}"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class OrderItem(SafeBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="ordered_products",verbose_name="O'yinchoq nomi:")
    quantity = models.PositiveIntegerField(default=1, verbose_name='Buyurtma soni:')
    color = models.CharField(choices=COLOR_CHOICES, default=COLOR_CHOICES[0][0], max_length=20, verbose_name="O'yinchoq rangi:")
   

    class Meta:
        verbose_name = "Buyurtmadagi o'yinchoq"
        verbose_name_plural = "Buyurtmadagi o'yinchoqlar"

    def __str__(self):
        return self.product.name


class CommentProducts(SafeBaseModel):
    product = models.ForeignKey(Products, related_name="comments", on_delete=models.CASCADE)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=0)
    


class LikedProducts(SafeBaseModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
