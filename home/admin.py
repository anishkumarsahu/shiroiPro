from django.contrib import admin
from .models import *
# Register your models here.


class StatusAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'isDeleted','datetime','lastUpdatedOn']

admin.site.register(Status, StatusAdmin)


class DepositItemAdmin(admin.TabularInline):
    model = DepositItem
    extra = 0


class DepositAdmin(admin.ModelAdmin):
    search_fields = ['depositSerialID','customerName','phone','address']
    list_display = ['depositSerialID','customerName','phone','address','depositDate','statusID','totalAmount','clearanceDate', 'isDeleted', 'datetime']

    inlines = (DepositItemAdmin,)
admin.site.register(Deposit, DepositAdmin)



class CashBookAdmin(admin.ModelAdmin):
    search_fields = ['remark','transactionType']
    list_display = ['remark','transactionType','amount', 'totalCredit', 'totalDebit','balanceThatTime','availableBalance', 'isDeleted','datetime','lastUpdatedOn']

admin.site.register(CashBook, CashBookAdmin)



class InterestAdmin(admin.ModelAdmin):
    search_fields = ['remark','amount']
    list_display = ['depositID','remark','amount', 'isDeleted','datetime','lastUpdatedOn']

admin.site.register(Interest, InterestAdmin)
