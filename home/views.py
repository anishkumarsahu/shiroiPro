import sys
from datetime import datetime

from django.db.models import Sum
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
        try:
            depo = Deposit.objects.last()
            depo = 'SS' + str(depo.pk + 1).zfill(5)
        except:
            depo ='SS00001'

        context ={
            'ID': depo
        }
        return render(request, 'home/newDepost.html', context)
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
        context = {
            'instance': instance,
            'items': items
        }

        return render(request, 'home/depositDetail.html', context)
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
        depo = Deposit.objects.filter(depositDate__icontains=datetime.today().date()).aggregate(Sum('totalAmount'))
        depo_item = DepositItem.objects.filter(withdrawalDate__icontains=datetime.today().date()).aggregate(Sum('total'))
        if depo_item['total__sum'] is None:
            inflow = 0
        else:
            inflow = depo_item['total__sum']

        if depo['totalAmount__sum'] is None:
            outflow = 0
        else:
            outflow = depo['totalAmount__sum']
        context = {
            'in':inflow,
            'out':outflow,
            'total':inflow-outflow,
            'date':datetime.today().date(),

        }

        return render(request, 'home/dailyReport.html',context)
    else:
        return redirect('homeApp:loginPage')


def print_billA5(request, *args, **kwargs):
    query = request.GET.get('q')

    depo = Deposit.objects.get(pk=int(query))
    depo_list = DepositItem.objects.filter(depositID_id=int(query))

    context = {
        'left': 8 - depo_list.count(),
        'loo': str().zfill(8- depo_list.count() - 1),
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
    depo_list = DepositItem.objects.filter(depositID_id=int(query))

    context = {
        'left': 8 - depo_list.count(),
        'loo': str().zfill(8 - depo_list.count() - 1),
        'TotalInWords': num2words(int(depo.totalAmountPaid)),
        'depo': depo,
        'depo_list': depo_list

    }
    return render(request, 'home/WithPrintA5.html', context)


def with_print_billA4(request, *args, **kwargs):
    query = request.GET.get('q')

    depo = Deposit.objects.get(pk=int(query))
    depo_list = DepositItem.objects.filter(depositID_id=int(query))

    context = {
        'left': 8 - depo_list.count(),
        'loo': str().zfill(8 - depo_list.count() - 1),
        'TotalInWords': num2words(int(depo.totalAmountPaid)),
        'depo': depo,
        'depo_list': depo_list

    }
    return render(request, 'home/WithPrintA4.html', context)
