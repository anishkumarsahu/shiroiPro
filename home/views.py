import sys
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core import management

# Create your views here.
# Create your views here.
from activation.models import Validity
from activation.views import is_activated
from home.numberToWord import num2words
from .models import *


def dashboard(request):
    if request.user.is_authenticated:
        try:
            val = Validity.objects.last()
            message = "Your License is Valid till {}".format(val.expiryDate.strftime('%d-%m-%Y'))
        except:
            message = "You are using a trial version."

        context = {
            'message': message
        }

        return render(request, 'home/dashboard.html', context)
    else:
        return redirect('homeApp:loginPage')


@is_activated()
def index(request):
    if request.user.is_authenticated:
        return render(request, 'home/index.html')
    else:
        return redirect('homeApp:loginPage')


def loginPage(request):
    if not request.user.is_authenticated:
        return render(request, 'home/login.html')
    else:
        return redirect('homeApp:dashboard')


@is_activated()
def new_deposit(request):
    if request.user.is_authenticated:
        depo = Deposit.objects.filter(isDeleted=False).count()
        depo = 'SS' + str(depo + 1).zfill(5)

        context = {
            'ID': depo
        }
        return render(request, 'home/newDepost.html', context)
    else:
        return redirect('homeApp:loginPage')


@is_activated()
def edit_deposit(request, id=None):
    if request.user.is_authenticated:
        instance = get_object_or_404(Deposit, pk = int(id))
        items = DepositItem.objects.filter(depositID_id = instance.pk)
        interests = Interest.objects.filter(depositID_id=instance.pk, isDeleted=False)

        context = {
            'instance': instance,
            'items': items,
            'interests': interests
        }
        return render(request, 'home/editDepost.html', context)
    else:
        return redirect('homeApp:loginPage')


@is_activated()
def deposit_history(request):
    if request.user.is_authenticated:
        return render(request, 'home/depositHistory.html')
    else:
        return redirect('homeApp:loginPage')

@is_activated()
def backup(request):
    if request.user.is_authenticated:
        return render(request, 'home/backup.html')
    else:
        return redirect('homeApp:loginPage')




@is_activated()
def deposit_detail(request, id=None):
    if request.user.is_authenticated:
        instance = get_object_or_404(Deposit, id=int(id))
        items = DepositItem.objects.filter(depositID_id=instance.pk)
        all_in = Interest.objects.filter(depositID_id=int(id))
        total = 0.0
        for i in all_in:
            total = total + i.amount
        context = {
            'instance': instance,
            'items': items,
            'total':total
        }

        return render(request, 'home/depositDetail.html', context)
    else:
        return redirect('homeApp:loginPage')



@is_activated()
def edit_deposit_detail(request, id=None):
    if request.user.is_authenticated:
        instance = get_object_or_404(Deposit, id=int(id))
        items = DepositItem.objects.filter(depositID_id=instance.pk)
        interests = Interest.objects.filter(depositID_id=instance.pk, isDeleted=False)
        context = {
            'instance': instance,
            'items': items,
            'interests': interests
        }

        return render(request, 'home/editDepositDetail.html', context)
    else:
        return redirect('homeApp:loginPage')

@is_activated()
def download_backup(request, id=None):
    if request.user.is_authenticated:
        response = HttpResponse(content_type='text/json')
        response['Content-Disposition'] = 'attachment; filename="NextBillBackUp-{}.json"'.format(datetime.today())
        stdout_orig = sys.stdout
        sys.stdout = response
        management.call_command('dumpdata')
        sys.stdout = stdout_orig
        response.write(sys.stdout)
        return response
    else:
        return redirect('homeApp:loginPage')



def daily_report(request):
    if request.user.is_authenticated:
        try:
            opening = CashBook.objects.filter(datetime__lt=datetime.today().date(), isDeleted__exact=False).last()
            o_balance = opening.availableBalance
        except:
            o_balance = 0.0
        try:
            current = CashBook.objects.all().last()
            c = current.availableBalance
        except:
            c = 0.0

        total_c = 0.0
        total_d = 0.0

        for cre in CashBook.objects.filter(datetime__icontains=datetime.today().date(), isDeleted__exact=False,transactionType__icontains='Credit'):
            total_c = total_c + cre.interest + cre.amount

        for d in CashBook.objects.filter(datetime__icontains=datetime.today().date(), isDeleted__exact=False,transactionType__icontains='Debit'):
            total_d = total_d + d.interest + d.amount

        context = {
            'o_balance': o_balance,
            'c': c,
            'date': datetime.today().date(),
            'credit':total_c,
            'debit':total_d,
            'available_balance': total_c - total_d

        }

        return render(request, 'home/dailyReport.html', context)
    else:
        return redirect('homeApp:loginPage')


def print_billA5(request, *args, **kwargs):
    query = request.GET.get('q')

    depo = Deposit.objects.get(pk=int(query))
    depo_list = DepositItem.objects.filter(depositID_id=int(query))

    context = {
        'left': 3 - depo_list.count(),
        'loo': str().zfill(3- depo_list.count() - 1),
        'TotalInWords': num2words(int(depo.totalAmount)),
        'depo': depo,
        'depo_list': depo_list

    }
    return render(request, 'home/PrintA5.html', context)


def print_billA4(request, *args, **kwargs):
    query = request.GET.get('q')

    depo = Deposit.objects.get(pk=int(query))
    depo_list = DepositItem.objects.filter(depositID_id=int(query))

    context = {
        'left': 10 - depo_list.count(),
        'loo': str().zfill(10 - depo_list.count() - 1),
        'TotalInWords': num2words(int(depo.totalAmount)),
        'depo': depo,
        'depo_list': depo_list

    }
    return render(request, 'home/PrintA4.html', context)


def with_print_billA5(request, *args, **kwargs):
    query = request.GET.get('q')

    depo = Deposit.objects.get(pk=int(query))
    depo_list = DepositItem.objects.filter(depositID_id=int(query), isDeleted__exact=False)
    int_list = Interest.objects.filter(depositID_id=int(query), isDeleted__exact=False)
    int_total = 0.0
    for i in int_list:
        int_total = int_total + i.amount

    try:
        a_paid = num2words(int(depo.totalAmountPaid))
    except:
        a_paid = 'Zero'

    try:
        a_paid_interest = num2words(int(int_total))
    except:
        a_paid_interest = 'Zero'

    context = {
        'left': 2 - depo_list.count(),
        'loo': str().zfill(2 - depo_list.count() - 1),
        'TotalInWords': a_paid,
        'depo': depo,
        'depo_list': depo_list,
        'a_paid_interest':a_paid_interest,
        'int_total':int_total,
        'int_list':int_list



    }
    return render(request, 'home/WithPrintA5.html', context)


def with_print_billA4(request, *args, **kwargs):
    query = request.GET.get('q')

    depo = Deposit.objects.get(pk=int(query))
    depo_list = DepositItem.objects.filter(depositID_id=int(query), isDeleted__exact=False)
    int_list = Interest.objects.filter(depositID_id=int(query), isDeleted__exact=False)
    int_total = 0.0
    for i in int_list:
        int_total = int_total + i.amount
    try:
        a_paid = num2words(int(depo.totalAmountPaid))
    except:
        a_paid = 'Zero'

    try:
        a_paid_interest = num2words(int(int_total))
    except:
        a_paid_interest = 'Zero'

    context = {
        'left': 2 - depo_list.count(),
        'loo': str().zfill(2 - depo_list.count() - 1),
        'TotalInWords': a_paid,
        'depo': depo,
        'depo_list': depo_list,
        'a_paid_interest':a_paid_interest,
        'int_total':int_total,
        'int_list':int_list



    }
    return render(request, 'home/WithPrintA4.html', context)
