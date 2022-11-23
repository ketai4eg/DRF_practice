from django.db import models
from django.contrib.auth.models import User


class Balance(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)


class Transactions(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=200)
    organisation = models.CharField(max_length=50)


class Categories(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    category_list = models.CharField(max_length=200)
