from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User, Product, Transaction, Service, Subscription, AgentProfile, ConsumerProfile, MerchantProfile, Bill, BillPayment
from .forms import CustomUserCreationForm, ProductForm
from rest_framework import viewsets, permissions
from .serializers import ProductSerializer, UserSerializer, AgentProfileSerializer, ConsumerProfileSerializer, MerchantProfileSerializer, TransactionSerializer, BillSerializer, BillPaymentSerializer, ServiceSerializer, SubscriptionSerializer
from decimal import Decimal, InvalidOperation
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = form.cleaned_data['role']  # Map role to user_type
            user.save()
            login(request, user)
            return redirect('splash')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def splash_page(request):
    return render(request, 'splash.html', {
        'username': request.user.username,
        'role': request.user.user_type if hasattr(request.user, 'user_type') else 'N/A'
    })

@login_required
def product_list(request):
    products = Product.objects.filter(merchant=request.user) if request.user.user_type == 'merchant' else []
    return render(request, 'product_list.html', {'products': products})

@login_required
def manage_products(request):
    if request.user.user_type != 'merchant':
        return HttpResponseForbidden("You are not authorized to access this page.")

    products = Product.objects.filter(merchant=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.merchant = request.user
            product.save()
            return redirect('manage_products')
    else:
        form = ProductForm()

    return render(request, 'manage_products.html', {'products': products, 'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, merchant=request.user)
    product.delete()
    return redirect('manage_products')

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, merchant=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'update_product.html', {'form': form, 'product': product})

@login_required
def transaction_history(request):
    if request.user.user_type != 'merchant':
        return HttpResponseForbidden("You are not authorized to access this page.")

    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'transaction_history.html', {'transactions': transactions})

@login_required
def balance_view(request):
    if request.user.user_type != 'merchant':
        return HttpResponseForbidden("You are not authorized to access this page.")

    transactions = Transaction.objects.filter(user=request.user)
    balance = sum(t.amount for t in transactions if t.transaction_type == 'cash_in') - \
              sum(t.amount for t in transactions if t.transaction_type == 'cash_out')

    return render(request, 'balance_view.html', {'balance': balance})

@login_required
def browse_products(request):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Fetch all products from merchants
    products = Product.objects.filter(merchant__user_type='merchant')
    return render(request, 'browse_products.html', {'products': products})

@login_required
def purchase_product(request, product_id):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    product = get_object_or_404(Product, id=product_id)
    consumer_profile = request.user.consumer_profile

    # Check if the consumer has enough balance
    if consumer_profile.balance < product.price:
        return HttpResponseForbidden("You do not have enough balance to purchase this product.")

    # Deduct the product price from the consumer's balance
    consumer_profile.balance -= product.price
    consumer_profile.save()

    # Add the product price to the merchant's balance
    merchant_profile = product.merchant.merchant_profile
    merchant_profile.balance += product.price
    merchant_profile.save()

    # Create a transaction for the consumer
    Transaction.objects.create(
        transaction_type='cash_out',
        user=request.user,
        amount=product.price,
        status='completed',
        reference_id=f'PUR-{product.id}-{request.user.id}-{uuid.uuid4()}'
    )

    # Create a transaction for the merchant
    Transaction.objects.create(
        transaction_type='cash_in',
        user=product.merchant,
        amount=product.price,
        status='completed',
        reference_id=f'SALE-{product.id}-{product.merchant.id}-{uuid.uuid4()}'
    )

    # Show confirmation on browse_products
    products = Product.objects.filter(merchant__user_type='merchant')
    return render(request, 'browse_products.html', {'products': products, 'purchase_success': True})

@login_required
def browse_services(request):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    services = Service.objects.all()
    return render(request, 'browse_services.html', {'services': services})

@login_required
def subscribe_service(request, service_id):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    service = get_object_or_404(Service, id=service_id)
    Subscription.objects.create(
        consumer=request.user,
        service=service
    )
    return redirect('browse_services')

@login_required
def consumer_transaction_history(request):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'consumer_transaction_history.html', {'transactions': transactions})

@login_required
def consumer_balance_view(request):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    transactions = Transaction.objects.filter(user=request.user)
    balance = sum(t.amount for t in transactions if t.transaction_type == 'cash_in') - \
              sum(t.amount for t in transactions if t.transaction_type == 'cash_out')

    return render(request, 'consumer_balance_view.html', {'balance': balance})

@login_required
def recharge_balance(request):
    if request.user.user_type != 'consumer':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(amount)  # Convert to Decimal instead of float
            if amount <= 0:
                return HttpResponseForbidden("Invalid amount. Please enter a positive value.")

            # Update the consumer's balance
            consumer_profile = request.user.consumer_profile
            consumer_profile.balance += amount
            consumer_profile.save()

            # Create a transaction for the recharge
            Transaction.objects.create(
                transaction_type='cash_in',
                user=request.user,
                amount=amount,
                status='completed',
                reference_id=f'RECHARGE-{uuid.uuid4()}'  # Ensure unique reference_id
            )

            return redirect('consumer_balance_view')
        except (ValueError, InvalidOperation):
            return HttpResponseForbidden("Invalid amount. Please enter a numeric value.")

    return render(request, 'recharge_balance.html')

@login_required
def accept_cash_payment(request):
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        consumer_username = request.POST.get('consumer_username')
        amount = request.POST.get('amount')
        try:
            consumer = User.objects.get(username=consumer_username, user_type='consumer')
            amount = Decimal(amount)
            if amount <= 0:
                return HttpResponseForbidden("Invalid amount. Please enter a positive value.")

            # Update the consumer's balance
            consumer_profile = consumer.consumer_profile
            consumer_profile.balance += amount
            consumer_profile.save()

            # Create a transaction for the consumer
            Transaction.objects.create(
                transaction_type='cash_in',
                user=consumer,
                amount=amount,
                status='completed',
                reference_id=f'CASHIN-{uuid.uuid4()}'
            )

            # Create a transaction for the agent
            Transaction.objects.create(
                transaction_type='cash_in',
                user=request.user,  # The agent performing the cash-in
                amount=amount,
                status='completed',
                reference_id=f'AGENTCASHIN-{uuid.uuid4()}'
            )

            return render(request, 'accept_cash_payment.html', {
                'success_message': f"Successfully added ${amount} to {consumer.username}'s balance."
            })
        except (User.DoesNotExist, ValueError, InvalidOperation):
            return render(request, 'accept_cash_payment.html', {
                'error_message': "Invalid consumer username or amount."
            })

    return render(request, 'accept_cash_payment.html')

@login_required
def cash_out_consumer(request):
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        consumer_username = request.POST.get('consumer_username')
        amount = request.POST.get('amount')
        try:
            consumer = User.objects.get(username=consumer_username, user_type='consumer')
            amount = Decimal(amount)
            if amount <= 0:
                return HttpResponseForbidden("Invalid amount. Please enter a positive value.")

            consumer_profile = consumer.consumer_profile

            # Check if the consumer has enough balance
            if consumer_profile.balance < amount:
                return render(request, 'cash_out_consumer.html', {
                    'error_message': f"Consumer {consumer.username} does not have enough balance."
                })

            # Deduct the amount from the consumer's balance
            consumer_profile.balance -= amount
            consumer_profile.save()

            # Create a transaction for the cash-out
            Transaction.objects.create(
                transaction_type='cash_out',
                user=consumer,
                amount=amount,
                status='completed',
                reference_id=f'CASHOUT-{uuid.uuid4()}'
            )

            # Create a transaction for the agent
            Transaction.objects.create(
                transaction_type='cash_out',
                user=request.user,  # The agent performing the cash-out
                amount=amount,
                status='completed',
                reference_id=f'AGENTCASHOUT-{uuid.uuid4()}'
            )

            return render(request, 'cash_out_consumer.html', {
                'success_message': f"Successfully deducted ${amount} from {consumer.username}'s balance."
            })
        except (User.DoesNotExist, ValueError, InvalidOperation):
            return render(request, 'cash_out_consumer.html', {
                'error_message': "Invalid consumer username or amount."
            })

    return render(request, 'cash_out_consumer.html')

@login_required
def agent_dashboard(request):
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("You are not authorized to access this page.")

    return render(request, 'agent_dashboard.html')

@login_required
def pay_bill_on_behalf(request):
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        consumer_username = request.POST.get('consumer_username')
        bill_type = request.POST.get('bill_type')
        account_number = request.POST.get('account_number')
        amount = request.POST.get('amount')
        try:
            consumer = User.objects.get(username=consumer_username, user_type='consumer')
            amount = Decimal(amount)
            if amount <= 0:
                return HttpResponseForbidden("Invalid amount. Please enter a positive value.")

            consumer_profile = consumer.consumer_profile

            # Check if the consumer has enough balance
            if consumer_profile.balance < amount:
                return render(request, 'pay_bill_on_behalf.html', {
                    'error_message': f"Consumer {consumer.username} does not have enough balance."
                })

            # Deduct the amount from the consumer's balance
            consumer_profile.balance -= amount
            consumer_profile.save()

            # Create a transaction for the bill payment
            Transaction.objects.create(
                transaction_type='bill_payment',
                user=consumer,
                amount=amount,
                status='completed',
                reference_id=f'BILLPAY-{uuid.uuid4()}'
            )

            # Create a transaction for the agent
            Transaction.objects.create(
                transaction_type='bill_payment',
                user=request.user,  # The agent performing the bill payment
                amount=amount,
                status='completed',
                reference_id=f'AGENTBILLPAY-{uuid.uuid4()}'
            )

            return render(request, 'pay_bill_on_behalf.html', {
                'success_message': f"Successfully paid ${amount} for {consumer.username}'s bill."
            })
        except (User.DoesNotExist, ValueError, InvalidOperation):
            return render(request, 'pay_bill_on_behalf.html', {
                'error_message': "Invalid consumer username or amount."
            })

    return render(request, 'pay_bill_on_behalf.html')

@login_required
def agent_transaction_history(request):
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'GET':
        # Display all transactions related to the agent by default
        transactions = Transaction.objects.filter(user=request.user)
        return render(request, 'agent_transaction_history.html', {
            'transactions': transactions
        })

    if request.method == 'POST':
        consumer_username = request.POST.get('consumer_username')
        try:
            consumer = User.objects.get(username=consumer_username, user_type='consumer')
            transactions = Transaction.objects.filter(user=consumer)
            return render(request, 'agent_transaction_history.html', {
                'consumer_username': consumer.username,
                'transactions': transactions
            })
        except User.DoesNotExist:
            return render(request, 'agent_transaction_history.html', {
                'error_message': "Consumer not found. Please check the username."
            })

    return render(request, 'agent_transaction_history.html')

@login_required
def agent_consumer_balance_view(request):
    if request.user.user_type != 'agent':
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        consumer_username = request.POST.get('consumer_username')
        try:
            consumer = User.objects.get(username=consumer_username, user_type='consumer')
            consumer_profile = consumer.consumer_profile
            return render(request, 'agent_consumer_balance_view.html', {
                'consumer_username': consumer.username,
                'balance': consumer_profile.balance
            })
        except User.DoesNotExist:
            return render(request, 'agent_consumer_balance_view.html', {
                'error_message': "Consumer not found. Please check the username."
            })

    return render(request, 'agent_consumer_balance_view.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        return Response({"message": "Login successful", "user_id": user.id})
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user_type = request.data.get('user_type')
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password, user_type=user_type)
    return Response({"message": "Signup successful", "user_id": user.id})

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    username = request.data.get('username')
    new_password = request.data.get('new_password')
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_profile(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "user_type": user.user_type
    })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AgentProfileViewSet(viewsets.ModelViewSet):
    queryset = AgentProfile.objects.all()
    serializer_class = AgentProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'agent':
            return AgentProfile.objects.filter(user=user)
        return AgentProfile.objects.none()

class ConsumerProfileViewSet(viewsets.ModelViewSet):
    queryset = ConsumerProfile.objects.all()
    serializer_class = ConsumerProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'consumer':
            return ConsumerProfile.objects.filter(user=user)
        elif user.user_type == 'agent':
            username = self.request.query_params.get('username')
            if username:
                return ConsumerProfile.objects.filter(user__username=username)
        return ConsumerProfile.objects.none()

class MerchantProfileViewSet(viewsets.ModelViewSet):
    queryset = MerchantProfile.objects.all()
    serializer_class = MerchantProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'merchant':
            return MerchantProfile.objects.filter(user=user)
        return MerchantProfile.objects.none()

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class BillPaymentViewSet(viewsets.ModelViewSet):
    queryset = BillPayment.objects.all()
    serializer_class = BillPaymentSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
