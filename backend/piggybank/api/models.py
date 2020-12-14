from django.db import models
from django.contrib.auth.models import User


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    isParent = models.BooleanField(default=True)


class Child(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    money = models.DecimalField(max_digits=9,decimal_places=2,default=0)
    isParent = models.BooleanField(default=False)



class PocketMoney(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9,decimal_places=2)
    start_date = models.DateField(blank=True)



class AccountHistory(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True)
    amount = models.DecimalField(max_digits=9,decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    money_after_transaction = models.DecimalField(max_digits=9,decimal_places=2,blank=True)



class Credit(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9,decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    is_accepted = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(blank=True)
    installment_amount = models.DecimalField(max_digits=9,decimal_places=2)
