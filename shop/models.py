from decimal import Decimal
from django.db.models import Avg,Sum
from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Products(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=14)
    discount = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    quantity = models.IntegerField()
    video_url = models.URLField(null=True, blank=True)

    @property
    def discounted_price(self):
        if self.discount > 0:
            discounted = self.price * Decimal(1 - self.discount / 100)
            return Decimal(f'{discounted}').quantize(Decimal('0.00'))
        return Decimal(f'{self.price}').quantize(Decimal('0.00'))

    def average_rating(self):
        avg_rating = self.comments.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    def sold(self):
        return self.ordered_products.aggregate(Sum("quantity"))[
                "quantity__sum"] or 0
    def __str__(self):
        return self.name


class ImageProducts(models.Model):
    product = models.ForeignKey(Products, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='toy_images/')


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('naxt','Naxt'),
        ('karta','Karta'),
    ]

    buyer_name = models.CharField(max_length=100, null=True, blank=True)
    buyer_surname = models.CharField(max_length=100, null=True, blank=True)
    buyer_number = models.CharField(max_length=100, null=True, blank=True)
    ordered_by = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    address = models.TextField()
    total_price = models.DecimalField(decimal_places=2, max_digits=14, default=0)
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=6, default='naxt')
    payment_link = models.URLField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ordered by {self.buyer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="ordered_products")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(decimal_places=2, max_digits=14, default=0)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.product.name

class CommentProducts(models.Model):
    product = models.ForeignKey(Products,related_name="comments", on_delete=models.CASCADE)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class LikedProducts(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)


class CartProduct(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    carted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('product', 'carted_by')