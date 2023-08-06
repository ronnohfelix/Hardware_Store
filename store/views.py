from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib import messages 
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
# Create your views here.

def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
       
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False) # new
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product) # new

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)
            
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

def signin_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(request, username=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Welcome back!")
            request.session['username'] = user.username
            return redirect('store')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('signin')

    return render(request, 'store/signin.html')


def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')  # Redirect back to the sign-up page

        # Check if a user with the given email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('signup')

        # Create the user account
        user = User.objects.create_user(username=email, email=email, password=password1)
        user.full_name = full_name
        user.save()

        # Create associated Customer instance
        customer = Customer(user=user)
        customer.save()
        
        messages.success(request, "Account created successfully. You can now sign in.")
        return redirect('signin')  # Redirect to the sign-in page

    return render(request, 'store/signup.html')

def logout_view(request):
    logout(request)
    if 'username' in request.session:
        del request.session['username']
    return redirect('store') 

def search_view(request):
    query = request.GET.get('q')
    results = []
    cartItems = 0  # Initialize cartItems here

    if query:
        data = cartData(request)
        cartItems = data['cartItems']
        results = Product.objects.filter(name__icontains=query)

    context = {
        'results': results,
        'cartItems': cartItems  # Include cartItems in the context
    }

    return render(request, 'store/search_results.html', context)


