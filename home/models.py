from django.db import models


# Create your models here.
class Status(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'A) Status List'

class Customer(models.Model):
    customerName = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)


    def __str__(self):
        return self.customerName

    class Meta:
        verbose_name_plural = 'E) Customer List'

class Item(models.Model):
    itemName = models.CharField(max_length=300, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.itemName

    class Meta:
        verbose_name_plural = 'E) Item List'


class Deposit(models.Model):
    depositSerialID = models.CharField(max_length=200, blank=True, null=True)
    oldID = models.CharField(max_length=200, blank=True, null=True)
    customerName = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    depositDate = models.DateField(blank=True, null=True)
    statusID = models.ForeignKey(Status, blank=True, null=True, on_delete=models.CASCADE)
    totalAmount = models.FloatField(default=0.0)
    totalAmountPaid = models.FloatField(default=0.0)
    totalInterestPaid = models.FloatField(default=0.0)
    clearanceDate = models.DateField(blank=True, null=True)
    totalWeight = models.CharField(max_length=200, blank=True, null=True)
    totalWeightL = models.CharField(max_length=200, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.depositSerialID

    class Meta:
        verbose_name_plural = 'B) Deposit List'


class DepositItem(models.Model):
    depositID = models.ForeignKey(Deposit, blank=True, null=True, on_delete=models.CASCADE)
    itemName = models.CharField(max_length=300, blank=True, null=True)
    weight = models.FloatField(default=0.0)
    tola =  models.IntegerField(default=0)
    san =  models.IntegerField(default=0)
    chaning =  models.IntegerField(default=0)
    itemRatePerTenGram = models.FloatField(default=0.0)
    interestRate = models.FloatField(default=0.0)
    description = models.TextField(blank=True, null=True)
    itemAmount = models.FloatField(default=0.0)
    isWithdrawn = models.BooleanField(default=False)
    withdrawalDate = models.DateField(blank=True, null=True)
    interestPaid = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)
    month = models.FloatField(default=0.0)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.depositID_id)

    class Meta:
        verbose_name_plural = 'C) Deposit Item List'


class CashBook(models.Model):
    remark = models.CharField(max_length=300, blank=True, null=True)
    depositID = models.CharField(max_length=100, default='N/A')
    customerName = models.CharField(max_length=100, default='N/A')
    interest = models.FloatField(default=0.0)
    transactionType = models.CharField(max_length=300, blank=True, null=True)
    amount = models.FloatField(default=0.0)
    balanceThatTime = models.FloatField(default=0.0)
    availableBalance = models.FloatField(default=0.0)
    totalCredit = models.FloatField(default=0.0)
    totalDebit = models.FloatField(default=0.0)
    isDeleted = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, auto_now=False)
    lastUpdatedOn = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.remark)

    class Meta:
        verbose_name_plural = 'D) CashBook List'
