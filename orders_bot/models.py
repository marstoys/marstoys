from django.db import models
from core.models.basemodel import SafeBaseModel
# Create your models here.



    
class ChannelsToSubscribe(SafeBaseModel):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.link
    
    class Meta:
        verbose_name = "Obuna bo'lish kerak bo'lgan kanallar"
        verbose_name_plural = "Obuna bo'lish kerak bo'lgan kanallar"

