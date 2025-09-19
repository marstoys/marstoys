from django.db import models
from core.models.basemodel import SafeBaseModel
# Create your models here.


class TelegramAdminsID(SafeBaseModel):
    tg_id = models.BigIntegerField()

    def __str__(self):
        return self.tg_id
