from django.urls import path

from .views import *
from .apiViews import *
#
# app_name = 'polls'
urlpatterns = [
    path('login/', loginPage, name='loginPage'),
    path('', dashboard, name='dashboard'),
    path('index', index, name='index'),
    path('postLogin/', postLogin, name='postLogin'),
    path('logout/', user_logout, name='logout'),

    path('new_deposit/', new_deposit, name='new_deposit'),
    path('deposit_history/', deposit_history, name='deposit_history'),
    path('deposit_detail/<int:id>/', deposit_detail, name='deposit_detail'),
    path('backup/', backup, name='backup'),
    path('download_backup/', download_backup, name='download_backup'),
    path('daily_flow/', daily_report, name='daily_report'),


    path('print_billA5/', print_billA5, name='print_billA5'),
    path('print_billA4/', print_billA4, name='print_billA4'),
    path('with_print_billA5/', with_print_billA5, name='with_print_billA5'),
    path('with_print_billA4/', with_print_billA4, name='with_print_billA4'),

    #API
    path('api/deposit_post/', deposit_post, name='deposit_post'),
    path('api/IncompleteDepositListJson/', IncompleteDepositListJson.as_view(), name='IncompleteDepositListJson'),
    path('api/PartiallyCompletedDepositListJson/', PartiallyCompletedDepositListJson.as_view(), name='PartiallyCompletedDepositListJson'),
    path('api/CompletedDepositListJson/', CompletedDepositListJson.as_view(), name='CompletedDepositListJson'),
    path('api/CashBookListJson/', CashBookListJson.as_view(), name='CashBookListJson'),

    path('api/delete_deposit/', delete_deposit, name='delete_deposit'),
    path('api/search_deposit/', search_deposit, name='search_deposit'),
    path('api/get_deposit_detail/<int:id>/', get_deposit_detail, name='get_deposit_detail'),
    path('api/item_closing_post/', item_closing_post, name='item_closing_post'),


    path('api/inflow_post/', inflow_post, name='inflow_post'),
    path('api/outflow_post/', outflow_post, name='outflow_post'),


    ]