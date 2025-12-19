from datetime import datetime, timedelta, time

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Sum, OuterRef, Subquery, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import *
from django.db import transaction


def add_current_time_to_date(given_date):
    """
    Adds the current local time to the given date and returns a datetime object.

    Args:
        given_date (date | datetime): The date to which the current time will be added.

    Returns:
        datetime: A datetime object with the given date and current time.
    """
    # Ensure we only take the date part if a datetime is passed
    if isinstance(given_date, datetime):
        given_date = given_date.date()
    # Get current local time
    current_time = datetime.now().time()
    # Combine given date with current time
    result = datetime.combine(given_date, current_time)
    return result

def convertGold(x):
    tola = x // 11.66
    rem_tola = x % 11.66
    san = rem_tola // (11.66 / 4)
    rem_san = rem_tola % (11.66 / 4)
    chaning = rem_san // (11.66 / 96)
    rem_chaning = rem_san % (11.66 / 96)


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

def get_customer_list(request):
    data = []
    q = request.GET.get('q')
    instance = Customer.objects.filter(Q(customerName__icontains=q) |Q(phone__icontains=q) |Q(address__icontains=q)  ,isDeleted__exact=False)

    for c in instance:
        data_dic = {
            'ID': c.pk,
            'CustomerName': '{}'.format(c.customerName ),
            'Phone': '{}'.format(c.phone),
            'Address': '{}'.format( c.address)

        }
        data.append(data_dic)
    return JsonResponse({'data': data}, safe=False)

def get_customer_detail_by_name(request):
    q = request.GET.get('q')
    try:

        instance = Customer.objects.get(pk__iexact=q, isDeleted__exact=False, )

        data = {
            'ID': instance.pk,
            'CustomerName': instance.customerName,
            'Phone': instance.phone,
            'Address': instance.address,


        }
    except:
        data = {
            'ID': '',
            'CustomerName': '',
            'Phone': '',
            'Address': '',
        }

    return JsonResponse({'data': data}, safe=False)


def get_item_list(request):
    data = []
    q = request.GET.get('q')
    instance = Item.objects.filter(Q(itemName__icontains=q) ,isDeleted__exact=False)

    for c in instance:
        data_dic = {
            'ID': c.pk,
            'ItemName': '{}'.format(c.itemName ),

        }
        data.append(data_dic)
    return JsonResponse({'data': data}, safe=False)

def get_item_detail_by_name(request):
    q = request.GET.get('q')
    try:

        instance = Item.objects.get(pk__iexact=q, isDeleted__exact=False, )

        data = {
            'ID': instance.pk,
            'ItemName': instance.itemName,



        }
    except:
        data = {
            'ID': '',
            'ItemName': '',

        }

    return JsonResponse({'data': data}, safe=False)


@transaction.atomic
@csrf_exempt
def deposit_post(request):
    cusID = request.POST.get("cusID")
    customerName = request.POST.get("customerName")
    phoneNumber = request.POST.get("phoneNumber")
    address = request.POST.get("address")
    pDate = request.POST.get("date")
    totalAmount = request.POST.get("totalAmount")
    datas = request.POST.get("datas")
    oldID = request.POST.get("oldID")
    totalWeight = request.POST.get("totalWeight")
    totalWeightL = request.POST.get("totalWeightL")
    remark = request.POST.get("remark")
    de = Deposit.objects.all().count()

    if cusID == 'N/A':
        cus = Customer()
        cus.customerName = customerName
        cus.phone = phoneNumber
        cus.address = address
        cus.save()

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
    depo.remark = remark
    depo.save()
    depo.depositSerialID = 'SS' + str(de+1).zfill(5)
    depo.save()
    splited_receive_item = datas.split("@")
    for item in splited_receive_item[:-1]:
        item_details = item.split('|')

        p = DepositItem()
        p.depositID_id = depo.pk
        p.itemName = item_details[1]
        try:
            it = Item.objects.get(itemName__iexact=item_details[1])
        except:
            it = Item()
            it.itemName = item_details[1]
            it.save()
        p.weight = float(item_details[2])
        p.itemRatePerTenGram = float(item_details[3])
        p.interestRate = float(item_details[4])
        p.description = item_details[5]
        p.itemAmount = float(item_details[6])
        p.tola = float(item_details[7])
        p.san = float(item_details[8])
        p.chaning = float(item_details[9])

        p.save()

    debit(0.0, depo.totalAmount, "New Deposit".format(depo.totalAmount, depo.depositSerialID), depo.depositSerialID,
          depo.customerName, add_current_time_to_date(depo.depositDate))
    return JsonResponse({'message': 'success', 'depoID': depo.pk}, safe=False)


@transaction.atomic
@csrf_exempt
def edit_deposit_post(request):
    dID = request.POST.get("dID")
    customerName = request.POST.get("customerName")
    phoneNumber = request.POST.get("phoneNumber")
    address = request.POST.get("address")
    pDate = request.POST.get("date")
    totalAmount = request.POST.get("totalAmount")
    datas = request.POST.get("datas")
    oldID = request.POST.get("oldID")
    totalWeight = request.POST.get("totalWeight")
    totalWeightL = request.POST.get("totalWeightL")
    remark = request.POST.get("remark")


    depo = Deposit.objects.get(id=int(dID))
    initial_amount = depo.totalAmount
    if initial_amount != float(totalAmount):
        credit(0.0, depo.totalAmount, "New Deposit Update".format(depo.totalAmount, depo.depositSerialID),
               depo.depositSerialID, depo.customerName,
               entryDateTime=add_current_time_to_date(datetime.strptime(pDate, '%d/%m/%Y')))
    depo.customerName = customerName
    depo.oldID = oldID
    depo.phone = phoneNumber
    depo.address = address
    depo.totalAmount = float(totalAmount)
    depo.depositDate = datetime.strptime(pDate, '%d/%m/%Y')
    depo.statusID_id = 1
    depo.totalWeight = totalWeight
    depo.totalWeightL = totalWeightL
    depo.remark = remark
    depo.save()
    del_items = DepositItem.objects.filter(depositID_id=depo.pk)
    del_items.delete()

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
    if initial_amount != float(totalAmount):
        debit(0.0, depo.totalAmount, "New Deposit Update".format(depo.totalAmount, depo.depositSerialID),
              depo.depositSerialID, depo.customerName, add_current_time_to_date(depo.depositDate))
    return JsonResponse({'message': 'success', 'depoID': depo.pk}, safe=False)




class  IncompleteDepositListJson(BaseDatatableView):
    order_columns = ['oldID', 'depositSerialID', 'customerName', 'phone', 'address', 'depositDate',
                     'statusID', 'totalAmount', 'totalInterestPaid', 'clearanceDate','remark', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        # startDate = datetime.strptime(sDate, '%d/%m/%Y')
        # endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if sDate =='All' and eDate == 'All':
            return Deposit.objects.filter(isDeleted__exact=False, statusID_id=1)
        else:
            startDate = datetime.strptime(sDate, '%d/%m/%Y')
            endDate = datetime.strptime(eDate, '%d/%m/%Y')
            return Deposit.objects.filter(isDeleted__exact=False, depositDate__gte=startDate.date(),
                                          depositDate__lte=endDate.date() + timedelta(days=1), statusID_id=1)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(remark__icontains=search) | Q(oldID__icontains=search) | Q(depositDate__icontains=search) | Q(
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

            action = ''' <span style="display:flex">   <a style="font-size:10px;"href="/edit_deposit/{}/" class="ui circular  icon button orange" data-tooltip="Edit" data-position="bottom right" data-inverted="">
                              <i class="edit icon"></i>
                             </a>
                             <a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue" data-tooltip="Receive Payment" data-position="bottom right" data-inverted="">
                               <i class="hand holding usd icon"></i>
                             </a><button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green" data-tooltip="Detail" data-position="bottom right" data-inverted="">
                               <i class="receipt icon"></i>
                             </button>
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px" data-tooltip="Delete" data-position="bottom right" data-inverted="">
                               <i class="trash alternate icon"></i>
                             </button> </span>'''.format(item.pk, item.pk, item.pk, item.pk),
            interest = datetime.today().date() - item.depositDate
            months = interest.days//30
            rem = interest.days%30
            if rem > 15:
                cal = (months + 1) * item.totalAmount * 0.02
            else:
                cal = (months + 0.5) * item.totalAmount * 0.02

            json_data.append([
                escape(item.oldID),
                escape(item.depositSerialID),
                escape(item.customerName),
                escape(item.phone),
                escape(item.address),
                escape(item.depositDate.strftime('%d-%m-%Y')),
                escape(item.statusID.name),
                escape(item.totalAmount),
                escape(round(cal,2)),
                escape(clearDate),
                escape(item.remark),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


class PartiallyCompletedDepositListJson(BaseDatatableView):
    order_columns = ['oldID', 'depositSerialID', 'customerName', 'phone', 'address', 'depositDate',
                     'statusID', 'totalAmount', 'totalInterestPaid', 'clearanceDate','remark', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        # startDate = datetime.strptime(sDate, '%d/%m/%Y')
        # endDate = datetime.strptime(eDate, '%d/%m/%Y')
        if sDate =='All' and eDate == 'All':
            return Deposit.objects.filter(isDeleted__exact=False, statusID_id=2)
        else:
            startDate = datetime.strptime(sDate, '%d/%m/%Y')
            endDate = datetime.strptime(eDate, '%d/%m/%Y')
            return Deposit.objects.filter(isDeleted__exact=False, depositDate__gte=startDate.date(),
                                      depositDate__lte=endDate.date() + timedelta(days=1), statusID_id=2)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(remark__icontains=search) |   Q(oldID__icontains=search) | Q(depositDate__icontains=search) | Q(
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

            action = '''<span style="display:flex">  
            <a style="font-size:10px;"href="/edit_deposit_detail/{}/" class="ui circular  icon button orange" data-tooltip="Edit" data-position="bottom right" data-inverted="">
                              <i class="edit icon"></i>
                             </a>
            <a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue" data-tooltip="Receive Payment" data-position="bottom right" data-inverted="">
                              <i class="hand holding usd icon"></i>
                             </a>
            <button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green" data-tooltip="Detail" data-position="bottom right" data-inverted="">
                               <i class="receipt icon"></i>
                             </button>
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px" data-tooltip="Delete" data-position="bottom right" data-inverted="">
                               <i class="trash alternate icon"></i>
                             </button> </span>'''.format(item.pk,item.pk, item.pk, item.pk),

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
                escape(item.remark),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


class CompletedDepositListJson(BaseDatatableView):
    order_columns = ['oldID', 'depositSerialID', 'customerName', 'phone', 'address', 'depositDate',
                     'statusID', 'totalAmount', 'totalInterestPaid', 'clearanceDate','remark', 'datetime', ]

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        if sDate =='All' and eDate == 'All':
            return Deposit.objects.filter(isDeleted__exact=False, statusID_id=3)
        else:
            startDate = datetime.strptime(sDate, '%d/%m/%Y')
            endDate = datetime.strptime(eDate, '%d/%m/%Y')
            return Deposit.objects.filter(isDeleted__exact=False, clearanceDate__gte=startDate.date(),
                                          clearanceDate__lte=endDate.date() + timedelta(days=1), statusID_id=3)



    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(remark__icontains=search) | Q(oldID__icontains=search) | Q(depositDate__icontains=search) | Q(
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

            action = '''<span style="display:flex">  
            <a style="font-size:10px;"href="/edit_deposit_detail/{}/" class="ui circular  icon button orange" data-tooltip="Edit" data-position="bottom right" data-inverted="">
                              <i class="edit icon"></i>
                             </a>
          
                             <button style="font-size:10px;" onclick = "GetSaleDetail('{}')" class="ui circular  icon button green" data-tooltip="Detail" data-position="bottom right" data-inverted="">
                               <i class="receipt icon"></i>
                             </button>
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px" data-tooltip="Delete" data-position="bottom right" data-inverted="">
                               <i class="trash alternate icon"></i>
                             </button> </span>'''.format(item.pk,item.pk, item.pk, item.pk),
            '''  <a style="font-size:10px;"href="/deposit_detail/{}/" class="ui circular  icon button blue" data-tooltip="Take Interest" data-position="bottom right" data-inverted="">
                               <i class="rupee sign icon"></i>
                             </a>'''

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
                escape(item.remark),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


@transaction.atomic
@csrf_exempt
def delete_deposit(request):
    if request.method == 'POST':
        id = request.POST.get("ID")
        depo = Deposit.objects.get(pk=int(id))
        depo.isDeleted = True
        depo.save()
        credit(0.0, depo.totalAmount,"Deposit Deleted", depo.depositSerialID, depo.customerName)

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
        'ClearanceRemark': instance.clearanceRemark if instance.clearanceRemark else "",
        'ActionType': instance.actionType if instance.actionType else "N/A",
        'TotalAmountPaid': instance.totalAmountPaid,
        "NewSerial": instance.newDepositSerialID if instance.newDepositSerialID else 'N/A',

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
    interests = Interest.objects.filter(depositID_id=instance.pk, isDeleted__exact=False)
    int_list = []
    for j in interests:
        int_dic = {
            'InterestID':j.pk,
            'Remark':j.remark,
            'Amount':j.amount,
            'Datetime':j.datetime.strftime('%d-%m-%Y %I:%M %p')
        }
        int_list.append(int_dic)
    data = {
        'Basic': basic,
        'Items': item_list,
        'Interest':int_list,

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


@transaction.atomic
@csrf_exempt
def item_closing_post(request):
    depositID = request.POST.get("depositID")
    totalAmount = request.POST.get("totalAmount")
    actionType = request.POST.get("actionType")
    month = request.POST.get("month")
    withdrawalDate = request.POST.get("withdrawalDate")
    itemInterestRate = request.POST.get("itemInterestRate")
    ICalculate = request.POST.get("ICalculate")
    interestPaid = request.POST.get("interestPaid")
    amountWithInterest = request.POST.get("amountWithInterest")
    InterestRemark = request.POST.get("InterestRemark")
    depo = Deposit.objects.get(pk=int(depositID))
    if actionType == "interest":
        depo.totalInterestPaid = depo.totalInterestPaid + float(interestPaid)
        depo.statusID_id = 3
        depo.totalAmountPaid = (depo.totalAmountPaid + float(amountWithInterest))
        depo.clearanceRemark = InterestRemark
        depo.clearanceDate = datetime.strptime(withdrawalDate, '%d/%m/%Y')
        depo.actionType = actionType
        depo.save()
        de = Deposit.objects.all().count()
        new_depo = Deposit()
        new_depo.customerName = depo.customerName
        new_depo.oldID = depo.oldID
        new_depo.phone = depo.phone
        new_depo.address = depo.address
        new_depo.depositDate = datetime.strptime(withdrawalDate, '%d/%m/%Y')
        new_depo.statusID_id = 1
        new_depo.totalAmount = depo.totalAmount
        new_depo.totalAmountPaid = 0
        new_depo.totalInterestPaid = 0
        new_depo.totalWeight = depo.totalWeight
        new_depo.totalWeightL = depo.totalWeightL
        new_depo.save()
        new_depo.depositSerialID = 'SS' + str(de + 1).zfill(5)
        new_depo.remark = depo.depositSerialID
        new_depo.save()
        depo.newDepositSerialID = new_depo.depositSerialID
        depo.save()
        deposit_items = DepositItem.objects.filter(depositID_id=int(depositID))
        for i in deposit_items:
            p = DepositItem()
            p.depositID_id = new_depo.pk
            p.itemName = i.itemName
            p.weight = i.weight
            p.itemRatePerTenGram = i.itemRatePerTenGram
            p.interestRate = i.interestRate
            p.description = i.description
            p.itemAmount = i.itemAmount
            p.tola = i.tola
            p.san = i.san
            p.chaning = i.chaning
            p.save()
            i.month = float(month)
            i.save()
        credit(interestPaid, new_depo.totalAmount, "Interest Paid", depo.depositSerialID, depo.customerName)
        debit(new_depo.totalAmountPaid, new_depo.totalAmount,
              f"New Deposit Against Interest Paid - {depo.depositSerialID}", new_depo.depositSerialID,
              new_depo.customerName)

    elif actionType == "repayment":
        depo.totalInterestPaid = depo.totalInterestPaid + float(interestPaid)
        depo.statusID_id = 3
        depo.totalAmountPaid = (depo.totalAmountPaid + float(amountWithInterest))
        depo.clearanceRemark = InterestRemark
        depo.clearanceDate = datetime.strptime(withdrawalDate, '%d/%m/%Y')
        depo.actionType = actionType
        depo.save()
        deposit_items = DepositItem.objects.filter(depositID_id=int(depositID))
        for i in deposit_items:
            i.isWithdrawn = True
            i.month = float(month)
            i.withdrawalDate = datetime.strptime(withdrawalDate, '%d/%m/%Y')
            i.save()
        credit(interestPaid, (float(amountWithInterest) - float(interestPaid)), "Interest Paid", depo.depositSerialID,
               depo.customerName, entryDateTime=add_current_time_to_date(depo.clearanceDate))

    # splited_receive_item = datas.split("@")
    # for item in splited_receive_item[:-1]:
    #     item_details = item.split('|')
    #
    #     p = DepositItem.objects.get(pk=int(item_details[0]))
    #     p.withdrawalDate = datetime.strptime(item_details[1], '%d/%m/%Y')
    #     p.interestPaid = float(item_details[2])
    #     p.total = float(item_details[3])
    #     p.month = float(item_details[4])
    #     p.isWithdrawn = True
    #     p.save()
    #     depo.totalInterestPaid = depo.totalInterestPaid + float(item_details[2])
    #     depo.save()
    #     credit(p.interestPaid, (p.total - p.interestPaid),"Deposit Paid",depo.depositSerialID, depo.customerName)
    #     # credit(p.interestPaid,"Interest Paid",depo.depositSerialID, depo.customerName)
    # totalItems = DepositItem.objects.filter(depositID_id=int(depositID)).count()
    # totalWithdrawn = DepositItem.objects.filter(depositID_id=int(depositID), isWithdrawn__exact=True).count()
    # totalPending = DepositItem.objects.filter(depositID_id=int(depositID), isWithdrawn__exact=False).count()
    # if totalItems == totalWithdrawn:
    #     depo.statusID_id = 3
    #     depo.clearanceDate = datetime.today().date()
    #     depo.save()
    # if totalWithdrawn < totalItems and totalPending < totalItems:
    #     depo.statusID_id = 2
    #     depo.save()

    return JsonResponse({'message': 'success'}, safe=False)


@transaction.atomic
@csrf_exempt
def item_closing_edit_post(request):
    depositID = request.POST.get("depositID")
    totalAmount = request.POST.get("totalAmount")
    datas = request.POST.get("datas")

    depo = Deposit.objects.get(pk=int(depositID))
    # depo.depositDate = datetime.strptime(pDate, '%d/%m/%Y')
    # depo.statusID_id = 1

    splited_receive_item = datas.split("@")
    for item in splited_receive_item[:-1]:
        item_details = item.split('|')

        p = DepositItem.objects.get(pk=int(item_details[0]))
        if p.isWithdrawn == True:
            depo.totalInterestPaid = (depo.totalInterestPaid - p.interestPaid)
            depo.totalAmountPaid = (depo.totalAmountPaid - (p.itemAmount + p.interestPaid))
            depo.save()
            debit(p.interestPaid, p.itemAmount, "Deposit Updated", depo.depositSerialID, depo.customerName)
            # debit(p.itemAmount, "Item Amount Update", depo.depositSerialID, depo.customerName)

        if item_details[6]== 'False':
            p.withdrawalDate = None
            p.interestPaid = 0
            p.total = 0
            p.month = 0
            p.isWithdrawn = False
            p.save()
        else:
            p.withdrawalDate = datetime.strptime(item_details[1], '%d/%m/%Y')
            p.interestPaid = float(item_details[2])
            p.total = float(item_details[3])
            p.month = float(item_details[4])
            p.isWithdrawn = True
            p.save()
            depo.totalInterestPaid = depo.totalInterestPaid + float(item_details[2])
            depo.save()
            credit(p.interestPaid,p.itemAmount ,"Item Update", depo.depositSerialID, depo.customerName)
            # credit(p.itemAmount, "Item Amount Update", depo.depositSerialID, depo.customerName)
            depo.totalAmountPaid = (depo.totalAmountPaid + float(totalAmount))
            depo.save()
    totalItems = DepositItem.objects.filter(depositID_id=int(depositID)).count()
    totalWithdrawn = DepositItem.objects.filter(depositID_id=int(depositID), isWithdrawn__exact=True).count()
    totalPending = DepositItem.objects.filter(depositID_id=int(depositID), isWithdrawn__exact=False).count()
    if totalItems == totalWithdrawn:
        depo.statusID_id = 3
        depo.clearanceDate = datetime.today().date()
        depo.save()
    elif totalWithdrawn < totalItems and totalPending < totalItems:
        depo.statusID_id = 2
        depo.clearanceDate = None
        depo.save()
    else:
        depo.statusID_id = 1
        depo.clearanceDate = None
        depo.save()
    return JsonResponse({'message': 'success'}, safe=False)


@transaction.atomic
@csrf_exempt
def inflow_post(request):
    remark = request.POST.get("Remark")
    amount = request.POST.get("Amount")
    customerNameIn = request.POST.get("customerNameIn")
    dateIn = request.POST.get("dateIn")
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
        book.entryDateTime = add_current_time_to_date(datetime.strptime(dateIn, '%d/%m/%Y'))
        book.customerName = customerNameIn
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
        book.customerName = customerNameIn
        book.entryDateTime = add_current_time_to_date(datetime.strptime(dateIn, '%d/%m/%Y'))
        book.save()

    return JsonResponse({'message': 'success'}, safe=False)


@transaction.atomic
@csrf_exempt
def outflow_post(request):
    remark = request.POST.get("Remark")
    amount = request.POST.get("Amount")
    customerNameOut = request.POST.get("customerNameOut")
    dateOut = request.POST.get("dateOut")
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
        book.customerName = customerNameOut
        book.entryDateTime = add_current_time_to_date(datetime.strptime(dateOut, '%d/%m/%Y'))
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = (last_book.balanceThatTime - float(amount))
        book.availableBalance = (last_book.availableBalance - float(amount))
        book.transactionType = tType
        book.customerName = customerNameOut
        book.totalDebit = (last_book.totalDebit + float(amount))
        book.entryDateTime = add_current_time_to_date(datetime.strptime(dateOut, '%d/%m/%Y'))
        book.save()

    return JsonResponse({'message': 'success'}, safe=False)


def credit(interest, amount, remark, serial='N/A', name='N/A', entryDateTime=None):
    initial = CashBook.objects.all().count()

    if initial == 0:
        book = CashBook()
        book.interest = float(interest)
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = float(amount) + float(interest)
        book.availableBalance = float(amount) + float(interest)
        book.transactionType = "Credit"
        book.totalCredit = book.totalCredit + float(amount) +float(interest)
        book.depositID = serial
        book.customerName = name
        book.entryDateTime = entryDateTime if entryDateTime else datetime.today().now()
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.interest = float(interest)
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = round((last_book.availableBalance + float(amount) + float(interest)),2)
        book.availableBalance = round((last_book.availableBalance + float(amount) + float(interest)),2)
        book.transactionType = "Credit"
        book.totalCredit = round((last_book.totalCredit + float(amount) + float(interest)),2)
        book.depositID = serial
        book.customerName = name
        book.entryDateTime = entryDateTime if entryDateTime else datetime.today().now()
        book.save()


def debit(interest, amount, remark, serial='N/A', name='N/A', entryDateTime=None):
    initial = CashBook.objects.all().count()

    if initial == 0:
        book = CashBook()
        book.interest = float(interest)
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = -float(amount)  - float(interest)
        book.availableBalance = -float(amount)  - float(interest)
        book.transactionType = "Debit"
        book.totalDebit = book.totalDebit + float(amount)  + float(interest)
        book.depositID = serial
        book.customerName = name
        book.entryDateTime = entryDateTime if entryDateTime else datetime.today().now()
        book.save()
    else:
        last_book = CashBook.objects.last()
        book = CashBook()
        book.interest = float(interest)
        book.amount = float(amount)
        book.remark = remark
        book.balanceThatTime = round((last_book.balanceThatTime - float(amount)  - float(interest)),2)
        book.availableBalance = round((last_book.availableBalance - float(amount) - float(interest)),2)
        book.transactionType = "Debit"
        book.totalDebit = round((last_book.totalDebit + float(amount) + float(interest)),2)
        book.depositID = serial
        book.customerName = name
        book.entryDateTime = entryDateTime if entryDateTime else datetime.today().now()
        book.save()


class CashBookDebitListJson(BaseDatatableView):
    order_columns = ['depositID', 'loanDate', 'customerName', 'amount', 'remark', 'entryDateTime']

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')

        # Subquery to get loanDate from Deposit model
        loan_date_subquery = Deposit.objects.filter(
            depositSerialID=OuterRef('depositID')
        ).values('depositDate')[:1]

        # Annotate the queryset with loanDate
        qs = CashBook.objects.annotate(
            loanDate=Subquery(loan_date_subquery)
        ).filter(
            isDeleted=False,
            entryDateTime__gte=startDate.date(),
            entryDateTime__lte=endDate.date() + timedelta(days=1),
            transactionType='Debit'
        )

        return qs
    def filter_queryset(self, qs):
        # Apply search filtering
        search = self.request.GET.get('search[value]', None)
        try:
            search = datetime.strptime(search, "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            search = search
        if search:
            qs = qs.filter(
                Q(depositID__icontains=search) | Q(customerName__icontains=search) |
                Q(amount__icontains=search) | Q(remark__icontains=search) |
                Q(transactionType__icontains=search) | Q(availableBalance__icontains=search) |
                Q(entryDateTime__icontains=search) | Q(totalCredit__icontains=search) |
                Q(loanDate__icontains=search)  # Add loanDate to the search
            )

        # Apply sorting
        order_column_index = self.request.GET.get('order[0][column]', '0')
        order_dir = self.request.GET.get('order[0][dir]', 'asc')
        order_column_name = self.order_columns[int(order_column_index)]

        if order_dir == 'asc':
            qs = qs.order_by(F(order_column_name).asc(nulls_last=True))
        else:
            qs = qs.order_by(F(order_column_name).desc(nulls_last=True))

        return qs

    def prepare_results(self, qs):
        json_data = []
        total_amount = qs.aggregate(Sum('amount'))['amount__sum'] or 0

        for item in qs:
            action = '''<span style="display:flex">  
             <button style="font-size:10px;" class="ui circular icon button orange" onclick = "editCashbook('{}', '{}', '{}', '{}','{}', '{}')" data-tooltip="Edit" data-position="bottom right" data-inverted="">
                               <i class="edit icon"></i>
                              </button>
                              <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px" data-tooltip="Delete" data-position="bottom right" data-inverted="">
                                <i class="trash alternate icon"></i>
                              </button> </span>'''.format(item.pk, 0.0, item.amount, item.remark, item.customerName,
                                                          item.entryDateTime.strftime('%d/%m/%Y'), item.pk),

            json_data.append([
                escape(item.depositID),
                escape(item.loanDate.strftime('%d-%m-%Y') if item.loanDate else 'N/A'),
                escape(item.customerName),
                escape(item.amount),
                escape(item.remark),
                escape(item.entryDateTime.strftime('%d-%m-%Y %I:%M %p')),
                action
            ])

        # Return data with total amounts
        return {
            "data": json_data,
            "totalAmount": total_amount,
        }


class CashBookCreditListJson(BaseDatatableView):
    order_columns = ['depositID', 'loanDate', 'customerName', 'amount', 'interest', 'totalCredit', 'remark',
                     'entryDateTime']

    def get_initial_queryset(self):
        sDate = self.request.GET.get('startDate')
        eDate = self.request.GET.get('endDate')
        startDate = datetime.strptime(sDate, '%d/%m/%Y')
        endDate = datetime.strptime(eDate, '%d/%m/%Y')

        # Subquery to get loanDate from Deposit model
        loan_date_subquery = Deposit.objects.filter(
            depositSerialID=OuterRef('depositID')
        ).values('depositDate')[:1]

        # Annotate the queryset with loanDate
        qs = CashBook.objects.annotate(
            loanDate=Subquery(loan_date_subquery)
        ).filter(
            isDeleted=False,
            entryDateTime__gte=startDate.date(),
            entryDateTime__lte=endDate.date() + timedelta(days=1),
            transactionType='Credit'
        )

        return qs

    def filter_queryset(self, qs):
        # Apply search filtering
        search = self.request.GET.get('search[value]', None)
        try:
            search = datetime.strptime(search, "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            search = search

        if search:
            qs = qs.filter(
                Q(depositID__icontains=search) | Q(customerName__icontains=search) |
                Q(amount__icontains=search) | Q(remark__icontains=search) |
                Q(transactionType__icontains=search) | Q(availableBalance__icontains=search) |
                Q(entryDateTime__icontains=search) | Q(totalCredit__icontains=search) |
                Q(loanDate__icontains=search)  # Add loanDate to the search
            )

        # Apply sorting
        order_column_index = self.request.GET.get('order[0][column]', '0')
        order_dir = self.request.GET.get('order[0][dir]', 'asc')
        order_column_name = self.order_columns[int(order_column_index)]

        if order_dir == 'asc':
            qs = qs.order_by(F(order_column_name).asc(nulls_last=True))
        else:
            qs = qs.order_by(F(order_column_name).desc(nulls_last=True))

        return qs

    def prepare_results(self, qs):
        json_data = []
        total_amount = qs.aggregate(Sum('amount'))['amount__sum'] or 0
        total_interest = qs.aggregate(Sum('interest'))['interest__sum'] or 0

        for item in qs:
            action = '''<span style="display:flex">  
             <button style="font-size:10px;" class="ui circular icon button orange" onclick = "editCashbook('{}','{}','{}','{}','{}','{}')" data-tooltip="Edit" data-position="bottom right" data-inverted="">
                               <i class="edit icon"></i>
                              </button>
                              <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px" data-tooltip="Delete" data-position="bottom right" data-inverted="">
                                <i class="trash alternate icon"></i>
                              </button> </span>'''.format(item.pk, item.interest, item.amount, item.remark,
                                                          item.customerName, item.entryDateTime.strftime('%d/%m/%Y'),
                                                          item.pk),

            json_data.append([
                escape(item.depositID),
                escape(item.loanDate.strftime('%d-%m-%Y') if item.loanDate else 'N/A'),
                escape(item.customerName),
                escape(item.amount),
                escape(item.interest),
                escape(round(item.amount + item.interest, 2)),
                escape(item.remark),
                escape(item.entryDateTime.strftime('%d-%m-%Y %I:%M %p')),
                action

            ])

        # Return data with total amounts
        return {
            "data": json_data,
            "totalAmount": total_amount,
            "totalInterest": total_interest
        }


@transaction.atomic
@csrf_exempt
def take_interest_post(request):
    inPaidAmount = request.POST.get("inPaidAmount")
    inDepositID = request.POST.get("inDepositID")
    inRemark = request.POST.get("inRemark")


    ins = Interest()
    ins.depositID_id  = int(inDepositID)
    ins.amount = float(inPaidAmount)
    ins.remark = inRemark
    ins.save()
    credit(inPaidAmount, 0.0, "Interest Received", ins.depositID.depositSerialID, ins.depositID.customerName)

    all_in = Interest.objects.filter(depositID_id=int(inDepositID), isDeleted=False)
    total = 0.0
    for i in all_in:
        total = total + i.amount

    deposit = Deposit.objects.get(pk=ins.depositID.pk)
    deposit.totalInterestPaid = total
    deposit.save()



    return JsonResponse({'message': 'success', 'total':total}, safe=False)


@transaction.atomic
@csrf_exempt
def edit_interest_post(request):
    inPaidAmount = request.POST.get("inPaidAmount")
    inDepositID = request.POST.get("inDepositID")
    inRemark = request.POST.get("inRemark")
    try:
        ins = Interest.objects.get(pk=int(inDepositID))
        initial_interest = ins.amount
        ins.amount = float(inPaidAmount)
        ins.remark = inRemark
        ins.save()
        credit(inPaidAmount, 0.0, f"Interest Updated from {initial_interest} to {inPaidAmount}",
               ins.depositID.depositSerialID, ins.depositID.customerName)
        debit(initial_interest, 0.0, f"Interest Updated from {initial_interest} to {inPaidAmount}",
              ins.depositID.depositSerialID, ins.depositID.customerName)

        all_in = Interest.objects.filter(depositID_id=int(ins.depositID.pk), isDeleted=False)
        total = 0.0
        for i in all_in:
            total = total + i.amount

        deposit = Deposit.objects.get(pk=ins.depositID.pk)
        deposit.totalInterestPaid = total
        deposit.save()
        return JsonResponse({'message': 'success', 'total': total}, safe=False)
    except:
        return JsonResponse({'message': 'error'}, safe=False)


@transaction.atomic
@csrf_exempt
def delete_interest_post(request):
    interestID = request.POST.get("interestID")
    try:
        ins = Interest.objects.get(pk=int(interestID))
        ins.isDeleted = True
        ins.save()
        debit(ins.amount, 0.0, f"Interest detail Deleted", ins.depositID.depositSerialID, ins.depositID.customerName)

        all_in = Interest.objects.filter(depositID_id=int(ins.depositID.pk), isDeleted=False)
        total = 0.0
        for i in all_in:
            total = total + i.amount

        deposit = Deposit.objects.get(pk=ins.depositID.pk)
        deposit.totalInterestPaid = total
        deposit.save()
        return JsonResponse({'message': 'success', 'total': total}, safe=False)
    except:
        return JsonResponse({'message': 'error'}, safe=False)


@require_GET
def get_deposits_search(request):
    query = request.GET.get('query', '').strip().lower()
    deposits = (
        Deposit.objects
        .filter(Q(depositSerialID__icontains=query) | Q(customerName__icontains=query), isDeleted=False)
        .select_related('statusID')
        .values(
            'pk', 'depositSerialID', 'customerName', 'statusID__name', 'depositDate'
        )
    )

    data = [
        {
            'id': d['pk'],
            'depositID': d['depositSerialID'],
            'name': d['customerName'],
            'statusID': d['statusID__name'],
            'depositDate': d['depositDate'].strftime('%d-%m-%Y'),
        }
        for d in deposits
    ]

    return JsonResponse(data, safe=False)


@transaction.atomic
@csrf_exempt
def delete_cashbook_entry(request):
    if request.method == 'POST':
        id = request.POST.get("ID")
        depo = CashBook.objects.get(pk=int(id))
        depo.isDeleted = True
        depo.save()
        # credit(0.0, depo.totalAmount,"Deposit Deleted", depo.depositSerialID, depo.customerName)

        return JsonResponse({'message': 'success'}, safe=False)


@transaction.atomic
@csrf_exempt
def edit_cashbook_post(request):
    remark = request.POST.get("editRemark")
    id = request.POST.get("editID")
    amount = request.POST.get("editAmount")
    interest = request.POST.get("editInterest")
    editCustomerName = request.POST.get("editCustomerName")
    editEntryDateTime = request.POST.get("editEntryDateTime")
    try:
        book = CashBook.objects.get(pk=int(id))
        book.amount = float(amount) if amount else 0.0
        book.interest = float(interest) if interest else 0.0
        book.remark = remark
        book.customerName = editCustomerName
        book.entryDateTime = add_current_time_to_date(datetime.strptime(editEntryDateTime, '%d/%m/%Y'))
        book.save()

        return JsonResponse({'message': 'success'}, safe=False)
    except:
        return JsonResponse({'message': 'error'}, safe=False)


@require_GET
def get_today_cashbook_balance(request):
    startDate = request.GET.get('startDate', '').strip()

    # Try different date formats
    date_formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y']
    convertedDate = None

    for date_format in date_formats:
        try:
            convertedDate = datetime.strptime(startDate, date_format).strftime('%Y-%m-%d')
            break
        except ValueError:
            continue

    if not convertedDate:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    data = CashBook.objects.filter(entryDateTime__date=convertedDate, isDeleted=False)
    credit = 0.0
    debit = 0.0
    for i in data:
        if i.transactionType == 'Credit':
            credit = credit + i.amount + i.interest
        else:
            debit = debit + i.amount + i.interest
    context = {
        'credit': credit,
        'debit': debit,
        'balance': credit - debit,
        'date': startDate  # For debugging
    }
    return JsonResponse(context, safe=False)


class CustomerListJson(BaseDatatableView):
    order_columns = ['customerName', 'phone', 'address',
                     'datetime', 'lastUpdatedOn']

    def get_initial_queryset(self):
        return Customer.objects.filter(isDeleted__exact=False)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(customerName__icontains=search)
                | Q(phone__icontains=search) | Q(address__icontains=search)

            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            action = ''' <span style="display:flex">   <button style="font-size:10px;" onclick ="editCustomer('{}')" class="ui circular  icon button orange" data-tooltip="Edit" data-position="bottom right" data-inverted="">
                              <i class="edit icon"></i>
                             </button>
                        
                             <button style="font-size:10px;" onclick ="delSale('{}')" class="ui circular youtube icon button" style="margin-left: 3px" data-tooltip="Delete" data-position="bottom right" data-inverted="">
                               <i class="trash alternate icon"></i>
                             </button> </span>'''.format(item.pk, item.pk),
            json_data.append([
                escape(item.customerName),
                escape(item.phone),
                escape(item.address),
                escape(item.datetime.strftime('%d-%m-%Y %I:%M %p')),
                escape(item.lastUpdatedOn.strftime('%d-%m-%Y %I:%M %p')),
                action,

            ])
        return json_data


@csrf_exempt
def delete_customer(request):
    try:
        if request.method == 'POST':
            id = request.POST.get("ID")
            customer = Customer.objects.get(pk=id)
            customer.isDeleted = True
            customer.save()
            return JsonResponse({'message': 'success'}, safe=False)

    except:
        return JsonResponse({'message': 'error'}, safe=False)


def get_customer_detail(request, pk):
    try:
        customer = Customer.objects.get(pk=pk)
        data = {
            'customerName': customer.customerName,
            'phone': customer.phone,
            'address': customer.address,
            'id': customer.pk,

        }
        return JsonResponse({'data': data}, safe=False)
    except:
        return JsonResponse({'error': 'Customer not found'}, status=404)


def update_customer_detail(request):
    if request.method == 'POST':
        id = request.POST.get("EditId")
        customerName = request.POST.get("customerName")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        try:
            customer = Customer.objects.get(pk=id)
            customer.customerName = customerName
            customer.phone = phone
            customer.address = address
            customer.save()
            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def add_customer_detail(request):
    if request.method == 'POST':
        customerName = request.POST.get("customerName")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        try:
            customer = Customer()
            customer.customerName = customerName
            customer.phone = phone
            customer.address = address
            customer.save()
            return JsonResponse({'message': 'success'}, safe=False)
        except:
            return JsonResponse({'message': 'error'}, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)
