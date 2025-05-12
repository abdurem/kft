"""
URL configuration for kft_agent_networkk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from core.views import signup, splash_page, product_list, manage_products, delete_product, update_product, transaction_history, balance_view, browse_products, purchase_product, browse_services, subscribe_service, consumer_transaction_history, consumer_balance_view, recharge_balance, accept_cash_payment, cash_out_consumer, agent_dashboard, pay_bill_on_behalf, agent_transaction_history, agent_consumer_balance_view, UserViewSet, AgentProfileViewSet, ConsumerProfileViewSet, MerchantProfileViewSet, TransactionViewSet, BillViewSet, BillPaymentViewSet, ProductViewSet, ServiceViewSet, SubscriptionViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.views.generic.base import RedirectView
from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

router = DefaultRouter()
router.register(r'users', UserViewSet)
# router.register(r'agent-profiles', AgentProfileViewSet)
# router.register(r'consumer-profiles', ConsumerProfileViewSet)
# router.register(r'merchant-profiles', MerchantProfileViewSet)
# router.register(r'transactions', TransactionViewSet)
# router.register(r'bills', BillViewSet)
# router.register(r'bill-payments', BillPaymentViewSet)
# router.register(r'products', ProductViewSet)
# router.register(r'services', ServiceViewSet)
# router.register(r'subscriptions', SubscriptionViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="KFT Agent Network API",
        default_version='v1',
        description="API documentation for the KFT Agent Network",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', signup, name='signup'),
    path('splash/', splash_page, name='splash'),
]

urlpatterns += router.urls

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('product-list/', product_list, name='product_list'),
    path('manage-products/', manage_products, name='manage_products'),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),
    path('update-product/<int:product_id>/', update_product, name='update_product'),
    path('transaction-history/', transaction_history, name='transaction_history'),
    path('balance-view/', balance_view, name='balance_view'),
    path('browse-products/', browse_products, name='browse_products'),
    path('purchase-product/<int:product_id>/', purchase_product, name='purchase_product'),
    path('consumer-transaction-history/', consumer_transaction_history, name='consumer_transaction_history'),
    path('consumer-balance-view/', consumer_balance_view, name='consumer_balance_view'),
    path('recharge-balance/', recharge_balance, name='recharge_balance'),
    path('accept-cash-payment/', accept_cash_payment, name='accept_cash_payment'),
    path('cash-out-consumer/', cash_out_consumer, name='cash_out_consumer'),
    path('agent-dashboard/', agent_dashboard, name='agent_dashboard'),
    path('pay-bill-on-behalf/', pay_bill_on_behalf, name='pay_bill_on_behalf'),
    path('agent-transaction-history/', agent_transaction_history, name='agent_transaction_history'),
    path('agent-consumer-balance-view/', agent_consumer_balance_view, name='agent_consumer_balance_view'),
    path('accounts/logout/', RedirectView.as_view(url='/logout/')),
]
