from django.db import models
from core.models.basemodel import SafeBaseModel
# Create your models here.




class SMSToken(SafeBaseModel):
    token = models.TextField()

    def __str__(self):
        return self.token
