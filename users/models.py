from django.db import models
from core.models.basemodel import SafeBaseModel

class CustomUser(SafeBaseModel):
    username = models.CharField(unique=True, max_length=150,blank=True,null=True)
    first_name = models.CharField(max_length=100 )
    last_name = models.CharField(max_length=100 )
    phone_number = models.CharField(unique=True,max_length=12)
    address=models.TextField(null=True, blank=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.first_name
    
    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
