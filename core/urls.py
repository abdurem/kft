from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.browse_products, name='browse_products'),
    path('services/', views.browse_services, name='browse_services'),
    path('manage-products/', views.manage_products, name='manage_products'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('balance-view/', views.balance_view, name='balance_view'),
    path('recharge-balance/', views.recharge_balance, name='recharge_balance'),
    path('cash-out/', views.cash_out, name='cash_out'),
    path('pay-bill/', views.pay_bill, name='pay_bill'),
]