from django.db import models
from telegram import Update

# Create your models here.


class User(models.Model):
    chat_id = models.IntegerField(default=0)
    name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def get(cls, update: Update):
        return (
            tgUser := update.effective_user,
            user := cls.objects.get_or_create(chat_id=tgUser.id, defaults=dict(
                name=tgUser.full_name,
                username=tgUser.full_name
            ))[0],
            user.temp
        )


    @property
    def temp(self) -> "Temp":
        return Temp.objects.get_or_create(user=self)[0]


class Temp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    home_price = models.IntegerField(null=True, blank=True)
    startup_price = models.IntegerField(null=True, blank=True)
    percent_per_year = models.IntegerField(null=True, blank=True)
    credit_duration = models.IntegerField(null=True,blank=True)
