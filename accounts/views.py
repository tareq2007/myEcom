import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from .forms import CustomUserCreationForm, ProfileForm, UserForm
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from .utils import cookieCart, cartData,guestOrder
from django.conf import settings
from .utils import cartData  # Your existing helper

@login_required
def wishlist_view(request):
    profile = Profile.objects.get(user=request.user) if request.user.is_authenticated else None
    customer, created = Customer.objects.get_or_create(user=request.user)
    wishlist, created = Wishlist.objects.get_or_create(customer=customer)
    return render(request, 'accounts/wishlist.html', {'wishlist': wishlist, 'profile': profile})

@login_required
def add_to_wishlist(request, product_id):
    customer = Customer.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(customer=customer)
    wishlist.products.add(product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    customer = Customer.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.get(customer=customer)
    wishlist.products.remove(product)
    return redirect('wishlist')

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    customer, _ = Customer.objects.get_or_create(user=request.user)
    wishlist, _ = Wishlist.objects.get_or_create(customer=customer)

    wishlisted_ids = wishlist.products.values_list('id', flat=True)

    context = {
        'product': product,
        'wishlisted_ids': wishlisted_ids,
    }
    return render(request, 'accounts/product_detail.html', context)

@login_required
def toggle_wishlist(request, product_id):
    customer, _ = Customer.objects.get_or_create(user=request.user)
    wishlist, _ = Wishlist.objects.get_or_create(customer=customer)
    product = get_object_or_404(Product, pk=product_id)

    if product in wishlist.products.all():
        wishlist.products.remove(product)
    else:
        wishlist.products.add(product)

    return redirect('product_detail', pk=product_id)

@csrf_exempt
def sslcommerz_payment(request):
    if request.method == 'POST':
        data = cartData(request)
        order = data['order']

        post_data = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
            'total_amount': str(order.get_cart_total),
            'currency': 'BDT',
            'tran_id': str(order.id),
            'success_url': request.build_absolute_uri('/payment-success/'),
            'fail_url': request.build_absolute_uri('/payment-fail/'),
            'cancel_url': request.build_absolute_uri('/payment-cancel/'),
            'ipn_url': request.build_absolute_uri('/payment-ipn/'),

            'cus_name': request.user.get_full_name() if request.user.is_authenticated else "Guest",
            'cus_email': request.user.email if request.user.is_authenticated else "guest@example.com",
            'cus_add1': 'Some Address',
            'cus_city': 'Dhaka',
            'cus_postcode': '1212',
            'cus_country': 'Bangladesh',
            'cus_phone': '01700000000',

            'shipping_method': 'NO',
            'product_name': 'Cart Order',
            'product_category': 'Ecommerce',
            'product_profile': 'general',
        }

        response = requests.post('https://sandbox.sslcommerz.com/gwprocess/v4/api.php', data=post_data)
        response_data = response.json()

        if response_data.get('status') == 'SUCCESS':
            return redirect(response_data['GatewayPageURL'])
        else:
            return JsonResponse({'error': 'SSLCommerz failed', 'data': response_data})

    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
def payment_success(request):
    return render(request, 'accounts/payment_success.html')

@csrf_exempt
def payment_fail(request):
    return render(request, 'accounts/payment_fail.html')

@csrf_exempt
def payment_cancel(request):
    return render(request, 'accounts/payment_cancel.html')

def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    context = {'profile': profile}
    return render(request, 'accounts/user-profile.html', context)


@login_required(login_url='login')
def userAccount(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    completed_orders = Order.objects.filter(customer=request.user.customer, complete=True).order_by('-date_ordered')

    context = {'profile': profile, 'completed_orders': completed_orders}
    return render(request, 'accounts/account.html', context)


@login_required(login_url='login')
def editAccount(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('account')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'accounts/profile_form.html', context)


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST.get('username', '').lower()
        password = request.POST.get('password', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist')
            return render(request, 'accounts/login_register.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', 'store'))
        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'accounts/login_register.html')


def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')


def registerUser(request):
    if request.user.is_authenticated:
        return redirect('profiles')

    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')

            login(request, user)
            return redirect('store')
        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': 'register', 'form': form}
    return render(request, 'accounts/login_register.html', context)


def store(request):
    search_query = request.GET.get('search_query', '')
    profile = Profile.objects.get(user=request.user) if request.user.is_authenticated else None

    data = cartData(request)
    cart_items = data['cartItems']

    if search_query:
        products = Product.objects.filter(name__icontains=search_query)
    else:
        products = Product.objects.all()

    wishlisted_ids = set()
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(customer__user=request.user)
            wishlisted_ids = set(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass

    context = {
        'products': products,
        'cart_items': cart_items,
        'search_query': search_query,
        'profile': profile,
        'wishlisted_ids': wishlisted_ids,
    }
    return render(request, 'accounts/store.html', context)



def cart(request):
    profile = Profile.objects.get(user=request.user) if request.user.is_authenticated else None
    if request.user.is_authenticated:
        customer = getattr(request.user, 'customer', None)
        if not customer:
            customer = Customer.objects.create(user=request.user, name=request.user.get_full_name() or request.user.username, email=request.user.email)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cart_items = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    context = {'items': items,'order': order,'cart_items': cart_items,'profile': profile}
    return render(request, 'accounts/cart.html', context)


def checkout(request):
    profile = Profile.objects.get(user=request.user) if request.user.is_authenticated else None
    
    data = cartData(request)
    cart_items = data['cartItems']
    order = data['order']
    items = data['items']


    context = {'items': items,'order': order,'cart_items': cart_items,'profile': profile}
    return render(request, 'accounts/checkout.html', context)


@login_required(login_url='login')
def updateItem(request):
    data = json.loads(request.body)
    productId = data.get('productId')
    action = data.get('action')

    customer = getattr(request.user, 'customer', None)
    if not customer:
        customer = Customer.objects.create(user=request.user, name=request.user.get_full_name() or request.user.username, email=request.user.email)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    product = Product.objects.get(id=productId)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1

    order_item.quantity = max(order_item.quantity, 0)
    order_item.save()

    if order_item.quantity == 0:
        order_item.delete()

    return JsonResponse('Item was updated', safe=False)


@csrf_exempt
def processOrder(request):
    import traceback
    transaction_id = datetime.datetime.now().timestamp()

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    print("Incoming payment data:", data)

    try:
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

        return JsonResponse({'message': 'Payment submitted..'})
    
    except Exception as e:
        print("ERROR during order processing:")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
