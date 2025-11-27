from django.db import models
from core.models.basemodel import SafeBaseModel
# Create your models here.



    
class ChannelsToSubscribe(SafeBaseModel):
    chanel_name = models.CharField(max_length=255)
    link = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.link

