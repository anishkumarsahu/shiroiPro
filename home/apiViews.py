from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import *


def convertGold(x):
    tola = x // 11.66
    rem_tola = x % 11.66
    san = rem_tola // (11.66 / 4)
    rem_san = rem_tola % (11.66 / 4)
    chaning = rem_san // (11.66 / 96)
    rem_chaning = rem_san % (11.66 / 96)
    print(tola, san, chaning, rem_chaning)


def user_logout(request):
    logout(request)
    return redirect("homeApp:loginPage")


@csrf_exempt
def postLogin(request):
    if request.method == 'POST':
        username = request.POST.get('userName')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'success'}, safe=False)


        else:
            return JsonResponse({'message': 'fail'}, safe=False)
    else:
        return JsonResponse({'message': 'fail'}, safe=False)


@csrf_exempt
def deposit_post(request):
    customerName = request.POST.get("customerName")
    phoneNumber = request.POST.get("phoneNumber")
    address = request.POST.get("address")
    pDate = request.POST.get("date")
    totalAmount = request.POST.get("totalAmount")
    datas = request.POST.get("datas")
    oldID = request.POST.get("oldID")
    totalWeight = request.POST.get("totalWeight")
    totalWeightL = request.POST.get("totalWeightL")

    depo = Deposit()
    depo.customerName = customerName
    depo.oldID = oldID
    depo.phone = phoneNumber
    depo.address = address
    depo.totalAmount = float(totalAmount)
    depo.depositDate = datetime.strptime(pDate, '%d/%m/%Y')
    depo.statusID_id = 1
    depo.totalWeight = totalWeight
    depo.totalWeightL = totalWeightL
    depo.save()
    depo.depositSerialID = 'SS' + str(depo.pk).zfill(5)
    depo.save()
    splited_receive_item = datas.split("@")
    for item in splited_receive_item[:-1]:
        item_details = item.split('|')

        p = DepositItem()
        p.depositID_id = depo.pk
        p.itemName = item_details[1]
        p.weight = float(item_details[2])
        p.itemRatePerTenGram = float(item_details[3])
        p.interestRate = float(item_details[4])
        p.description = item_details[5]
        p.itemAmount = float(item_details[6])
        p.tola = float(item_details[7])
        p.san = float(item_details[8])
        p.chaning = float(item_details[9])

        p.save()
    debit(depo.totalAmount, "Given for amount Rs. {} with depositID {}".format(depo.totalAmount, depo.depositSerialID))
    return JsonResponse({'message': 'success', 'depoID': depo.pk}, safe=False)


class IncompleteDepositListJson(BaseDatatableView):
    order_columns = ['oldID', 'depositSerialID', 'customerName', 'phone', 'address', 'depositDate',
                     'statusID', 'totalAmount', 'totalInterestPaid', 'clearanceDate', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        return Deposit.objects.filter(isDeleted__exact=False, depositDate__gte=startDate.date(),
                                      depositDate__lte=endDate.date() + timedelta(days=1), statusID_id=1)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(oldID__icontains=search) | Q(depositDate__icontains=search) | Q(
                    depositSerialID__icontains=search) | Q(
                    customerName__icontains=search)
                | Q(phone__icontains=search) | Q(address__icontains=search) | Q(clearanceDate__icontains=search)
                | Q(statusID__name__icontains=search) | Q(totalAmount__icontains=search) | Q(
                    totalInterestPaid__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            if item.clearanceDate is None:
                clearDate = 'N/A'
            else:
                clearDate = item.clearanceDate

            action = '''<a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue">
                               <i class="rupee sign icon"></i>
                             </a><button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green">
                               <i class="receipt icon"></i>
                             </button>
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                               <i class="trash alternate icon"></i>
                             </button>'''.format(item.pk, item.pk, item.pk),

            json_data.append([
                escape(item.oldID),
                escape(item.depositSerialID),
                escape(item.customerName),
                escape(item.phone),
                escape(item.address),
                escape(item.depositDate.strftime('%d-%m-%Y')),
                escape(item.statusID.name),
                escape(item.totalAmount),
                escape(item.totalInterestPaid),
                escape(clearDate),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


class PartiallyCompletedDepositListJson(BaseDatatableView):
    order_columns = ['oldID', 'depositSerialID', 'customerName', 'phone', 'address', 'depositDate',
                     'statusID', 'totalAmount', 'totalInterestPaid', 'clearanceDate', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        return Deposit.objects.filter(isDeleted__exact=False, depositDate__gte=startDate.date(),
                                      depositDate__lte=endDate.date() + timedelta(days=1), statusID_id=2)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(oldID__icontains=search) | Q(depositDate__icontains=search) | Q(
                    depositSerialID__icontains=search) | Q(
                    customerName__icontains=search)
                | Q(phone__icontains=search) | Q(address__icontains=search) | Q(clearanceDate__icontains=search)
                | Q(statusID__name__icontains=search) | Q(totalAmount__icontains=search) | Q(
                    totalInterestPaid__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            if item.clearanceDate is None:
                clearDate = 'N/A'
            else:
                clearDate = item.clearanceDate

            action = '''<a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue">
                               <i class="rupee sign icon"></i>
                             </a>
            <button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green">
                               <i class="receipt icon"></i>
                             </button>
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                               <i class="trash alternate icon"></i>
                             </button>'''.format(item.pk, item.pk, item.pk),

            json_data.append([
                escape(item.oldID),
                escape(item.depositSerialID),
                escape(item.customerName),
                escape(item.phone),
                escape(item.address),
                escape(item.depositDate.strftime('%d-%m-%Y')),
                escape(item.statusID.name),
                escape(item.totalAmount),
                escape(item.totalInterestPaid),
                escape(clearDate),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


class CompletedDepositListJson(BaseDatatableView):
    order_columns = ['oldID', 'depositSerialID', 'customerName', 'phone', 'address', 'depositDate',
                     'statusID', 'totalAmount', 'totalInterestPaid', 'clearanceDate', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        return Deposit.objects.filter(isDeleted__exact=False, depositDate__gte=startDate.date(),
                                      depositDate__lte=endDate.date() + timedelta(days=1), statusID_id=3)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(oldID__icontains=search) | Q(depositDate__icontains=search) | Q(
                    depositSerialID__icontains=search) | Q(
                    customerName__icontains=search)
                | Q(phone__icontains=search) | Q(address__icontains=search) | Q(clearanceDate__icontains=search)
                | Q(statusID__name__icontains=search) | Q(totalAmount__icontains=search) | Q(
                    totalInterestPaid__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            if item.clearanceDate is None:
                clearDate = 'N/A'
            else:
                clearDate = item.clearanceDate.strftime('%d-%m-%Y')

            action = '''<a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue">
                               <i class="rupee sign icon"></i>
                             </a>
                             <button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green">
                               <i class="receipt icon"></i>
                             </button>
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
                               <i class="trash alternate icon"></i>
                             </button>'''.format(item.pk, item.pk, item.pk),

            json_data.append([
                escape(item.oldID),
                escape(item.depositSerialID),
                escape(item.customerName),
                escape(item.phone),
                escape(item.address),
                escape(item.depositDate.strftime('%d-%m-%Y')),
                escape(item.statusID.name),
                escape(item.totalAmount),
                escape(item.totalInterestPaid),
                escape(clearDate),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


@csrf_exempt
def delete_deposit(request):
    if request.method == 'POST':
        id = request.POST.get("ID")
        depo = Deposit.objects.get(pk=int(id))
        depo.isDeleted = True
        depo.save()

        return JsonResponse({'message': 'success'}, safe=False)


def get_deposit_detail(request, id=None):
    instance = get_object_or_404(Deposit, pk=id)
    basic = {
        'DepositSerialID': instance.depositSerialID + " (" +instance.oldID + ")",
        'Name': instance.customerName,
        'Phone': instance.phone,
        'Address': instance.address,
        'DepositDate': instance.depositDate,
        'Status': instance.statusID.name,
        'TotalAmount': instance.totalAmount,
        'TotalInterestPaid': instance.totalInterestPaid,
        'ClearanceDate': instance.clearanceDate,
        'TotalWeight': instance.totalWeight,
        'TotalWeightL': instance.totalWeightL,

    }
    items = DepositItem.objects.filter(depositID_id=instance.pk)
    item_list = []
    for i in items:
        item_dic = {
            'ItemID': i.pk,
            'ItemName': i.itemName,
            'Weight': i.weight,
            'ItemRatePerTenGram': i.itemRatePerTenGram,
            'InterestRate': i.interestRate,
            'Description': i.description,
            'ItemAmount': i.itemAmount,
            'IsWithdrawn': i.isWithdrawn,
            'WithdrawalDate': i.withdrawalDate,
            'InterestPaid': i.interestPaid,
            'WeightLocal': str(i.tola) +' T '+str(i.san) +' S '+str(i.chaning) +' C',

        }
        item_list.append(item_dic)

    data = {
        'Basic': basic,
        'Items': item_list

    }
    return JsonResponse({'data': data}, safe=False)


@csrf_exempt
def search_deposit(request):
    if request.method == 'POST':
        Search = request.POST.get("Search")
        try:
            depo = Deposit.objects.get(depositSerialID__iexact=Search, isDeleted__exact=False)
            return JsonResponse({'message': 'success', 'id': depo.pk}, safe=False)
        except:
            return JsonResponse({'message': 'fail'}, safe=False)


@csrf_exempt
def item_closing_post(request):
    depositID = request.POST.get("depositID")
    totalAmount = request.POST.get("totalAmount")
    datas = request.POST.get("datas")

    depo = Deposit.objects.get(pk=int(depositID))
    # depo.depositDate = datetime.strptime(pDate, '%d/%m/%Y')
    # depo.statusID_id = 1
    depo.totalAmountPaid = (depo.totalAmountPaid + float(totalAmount))
    depo.save()
    splited_receive_item = datas.split("@")
    for item in splited_receive_item[:-1]:
        item_details = item.split('|')

        p = DepositItem.objects.get(pk=int(item_details[0]))
        p.withdrawalDate = datetime.strptime(item_details[1], '%d/%m/%Y')
        p.interestPaid = float(item_details[2])
        p.total = float(item_details[3])
        p.month = float(item_details[4])
        p.isWithdrawn = True
        p.save()
        depo.totalInterestPaid = depo.totalInterestPaid + float(item_details[2])
        depo.save()
        credit(p.total,
               "Received an amount of Rs. {} with depositID {}".format(p.total, depo.depositSerialID))
    totalItems = DepositItem.objects.filter(depositID_id=int(depositID)).count()
    totalWithdrawn = DepositItem.objects.filter(depositID_id=int(depositID), isWithdrawn__exact=True).count()
    totalPending = DepositItem.objects.filter(depositID_id=int(depositID), isWithdrawn__exact=False).count()
    if totalItems == totalWithdrawn:
        depo.statusID_id = 3
        depo.clearanceDate = datetime.today().date()
        depo.save()
    if totalWithdrawn < totalItems and totalPending < totalItems:
        depo.statusID_id = 2
        depo.save()

    return JsonResponse({'message': 'success'}, safe=False)


@csrf_exempt
def inflow_post(request):
    remark = request.POST.get("Remark")
    amount = request.POST.get("Amount")
    tType = request.POST.get("tType")
    initial = CashBook.objects.all().count()

    if initial == 0:
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = float(amount)
        book.availableBalance = float(amount)
        book.transactionType = tType
        book.totalCredit = book.totalCredit + float(amount)
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = last_book.availableBalance + float(amount)
        book.availableBalance = last_book.availableBalance + float(amount)
        book.transactionType = tType
        book.totalCredit = last_book.totalCredit + float(amount)
        book.save()

    return JsonResponse({'message': 'success'}, safe=False)


@csrf_exempt
def outflow_post(request):
    remark = request.POST.get("Remark")
    amount = request.POST.get("Amount")
    tType = request.POST.get("tType")
    initial = CashBook.objects.all().count()

    if initial == 0:
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = -float(amount)
        book.availableBalance = -float(amount)
        book.transactionType = tType
        book.totalDebit = book.totalDebit + float(amount)
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = (last_book.balanceThatTime - float(amount))
        book.availableBalance = (last_book.availableBalance - float(amount))
        book.transactionType = tType
        book.totalDebit = (last_book.totalDebit + float(amount))
        book.save()

    return JsonResponse({'message': 'success'}, safe=False)


def credit(amount, remark):
    initial = CashBook.objects.all().count()

    if initial == 0:
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = float(amount)
        book.availableBalance = float(amount)
        book.transactionType = "Credit"
        book.totalCredit = book.totalCredit + float(amount)
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = round((last_book.availableBalance + float(amount)),2)
        book.availableBalance = round((last_book.availableBalance + float(amount)),2)
        book.transactionType = "Credit"
        book.totalCredit = round((last_book.totalCredit + float(amount)),2)
        book.save()


def debit(amount, remark):
    initial = CashBook.objects.all().count()

    if initial == 0:
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = -float(amount)
        book.availableBalance = -float(amount)
        book.transactionType = "Debit"
        book.totalDebit = book.totalDebit + float(amount)
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = round((last_book.balanceThatTime - float(amount)),2)
        book.availableBalance = round((last_book.availableBalance - float(amount)),2)
        book.transactionType = "Debit"
        book.totalDebit = round((last_book.totalDebit + float(amount)),2)
        book.save()


class CashBookDebitListJson(BaseDatatableView):
    order_columns = ['amount', 'remark', 'availableBalance', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        return CashBook.objects.filter(isDeleted__exact=False, datetime__gte=startDate.date(),
                                       datetime__lte=endDate.date() + timedelta(days=1), transactionType__exact='Debit')

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(transactionType__icontains=search) | Q(
                    availableBalance__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            # if item.transactionType == "Credit":
            #     t = '<button class="mini ui green button">Credit</button>'
            # else:
            #     t = '<button class="mini ui red button">Debit</button>'
            # action = '''<a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue">
            #                    <i class="rupee sign icon"></i>
            #                  </a>
            #                  <button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green">
            #                    <i class="receipt icon"></i>
            #                  </button>
            #                  <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
            #                    <i class="trash alternate icon"></i>
            #                  </button>'''.format(item.pk, item.pk, item.pk),

            json_data.append([

                escape(item.amount),
                escape(item.remark),
                escape(item.availableBalance),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
        return json_data


class CashBookCreditListJson(BaseDatatableView):
    order_columns = ['amount', 'remark', 'availableBalance', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')
        return CashBook.objects.filter(isDeleted__exact=False, datetime__gte=startDate.date(),
                                       datetime__lte=endDate.date() + timedelta(days=1),
                                       transactionType__exact='Credit')

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(amount__icontains=search) | Q(remark__icontains=search) | Q(transactionType__icontains=search) | Q(
                    availableBalance__icontains=search)
                | Q(datetime__icontains=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            # if item.transactionType == "Credit":
            #     t = '<button class="mini ui green button">Credit</button>'
            # else:
            #     t = '<button class="mini ui red button">Debit</button>'
            # action = '''<a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue">
            #                    <i class="rupee sign icon"></i>
            #                  </a>
            #                  <button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green">
            #                    <i class="receipt icon"></i>
            #                  </button>
            #                  <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px">
            #                    <i class="trash alternate icon"></i>
            #                  </button>'''.format(item.pk, item.pk, item.pk),

            json_data.append([

                escape(item.amount),
                escape(item.remark),
                escape(item.availableBalance),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),

            ])
        return json_data
