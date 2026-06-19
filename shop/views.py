import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Order, OrderItem

# --- TEMPLATE VIEWS (Serve HTML Pages) ---

def index_view(request):
    return render(request, 'shop/index.html')

def product_page_view(request, product_id):
    return render(request, 'shop/product.html', {'product_id': product_id})

def cart_page_view(request):
    return render(request, 'shop/cart.html')

def checkout_page_view(request):
    return render(request, 'shop/checkout.html')

def login_page_view(request):
    return render(request, 'shop/login.html')

def register_page_view(request):
    return render(request, 'shop/register.html')

def orders_page_view(request):
    return render(request, 'shop/orders.html')


# --- API VIEWS (JSON Endpoints) ---

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not password or not email:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        # Automatically login after registration
        login(request, user)
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'user': {'username': user.username, 'email': user.email}
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {'username': user.username, 'email': user.email}
            })
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_logout(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})

def api_auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {'username': request.user.username, 'email': request.user.email}
        })
    return JsonResponse({'authenticated': False})

def api_products(request):
    products = Product.objects.all()
    # Support simple search query
    query = request.GET.get('search', '')
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    
    product_list = []
    for p in products:
        product_list.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price),
            'image_url': p.image_url,
            'stock': p.stock
        })
    return JsonResponse({'products': product_list})

def api_product_detail(request, product_id):
    try:
        p = Product.objects.get(id=product_id)
        return JsonResponse({
            'product': {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': float(p.price),
                'image_url': p.image_url,
                'stock': p.stock
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

@csrf_exempt
def api_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method == 'GET':
        items = CartItem.objects.filter(user=request.user)
        cart_list = []
        for item in items:
            cart_list.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'image_url': item.product.image_url,
                'quantity': item.quantity,
                'stock': item.product.stock
            })
        return JsonResponse({'cart': cart_list})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))

            if not product_id:
                return JsonResponse({'error': 'Product ID required'}, status=400)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Product not found'}, status=404)

            # Check stock
            if product.stock < quantity:
                return JsonResponse({'error': f'Only {product.stock} items left in stock'}, status=400)

            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
            if not created:
                new_quantity = cart_item.quantity + quantity
                if product.stock < new_quantity:
                    return JsonResponse({'error': f'Only {product.stock} items left in stock'}, status=400)
                cart_item.quantity = new_quantity
            else:
                cart_item.quantity = quantity
            
            cart_item.save()
            return JsonResponse({'success': True, 'message': 'Cart updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity'))

            if not product_id or quantity is None:
                return JsonResponse({'error': 'Product ID and quantity required'}, status=400)

            if quantity <= 0:
                CartItem.objects.filter(user=request.user, product_id=product_id).delete()
                return JsonResponse({'success': True, 'message': 'Item removed from cart'})

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'error': 'Product not found'}, status=404)

            if product.stock < quantity:
                return JsonResponse({'error': f'Only {product.stock} items left in stock'}, status=400)

            cart_item = CartItem.objects.get(user=request.user, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'success': True, 'message': 'Cart item updated'})
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Item not in cart'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            # Can pass product_id as query parameter or JSON body
            product_id = request.GET.get('product_id')
            if not product_id:
                data = json.loads(request.body)
                product_id = data.get('product_id')

            CartItem.objects.filter(user=request.user, product_id=product_id).delete()
            return JsonResponse({'success': True, 'message': 'Item removed from cart'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_checkout(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        shipping_name = data.get('name')
        shipping_email = data.get('email')
        shipping_address = data.get('address')

        if not shipping_name or not shipping_email or not shipping_address:
            return JsonResponse({'error': 'All shipping fields are required'}, status=400)

        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        # Verify stock and calculate total price
        total_price = 0
        order_items_to_create = []

        for item in cart_items:
            product = item.product
            if product.stock < item.quantity:
                return JsonResponse({'error': f'Product "{product.name}" does not have enough stock'}, status=400)
            
            total_price += product.price * item.quantity
            order_items_to_create.append((product, item.quantity, product.price))

        # Create Order
        order = Order.objects.create(
            user=request.user,
            shipping_name=shipping_name,
            shipping_email=shipping_email,
            shipping_address=shipping_address,
            total_price=total_price,
            status='Pending'
        )

        # Create OrderItems and reduce stock
        for product, quantity, price in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=price,
                quantity=quantity
            )
            product.stock -= quantity
            product.save()

        # Clear cart
        cart_items.delete()

        return JsonResponse({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order.id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_orders(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_list = []
    for order in orders:
        items = []
        for item in order.items.all():
            items.append({
                'product_name': item.product_name,
                'price': float(item.price),
                'quantity': item.quantity
            })
        orders_list.append({
            'id': order.id,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': order.status,
            'total_price': float(order.total_price),
            'shipping_name': order.shipping_name,
            'shipping_address': order.shipping_address,
            'items': items
        })
    return JsonResponse({'orders': orders_list})
