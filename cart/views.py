from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.db import transaction

def index(request):
    """Display all user carts and allow cart selection"""
    if not request.user.is_authenticated:
        return redirect('accounts.login')
    
    user_carts = Cart.objects.filter(user=request.user)
    
    template_data = {
        'title': 'My Shopping Carts',
        'user_carts': user_carts,
    }
    return render(request, 'cart/index.html', {'template_data': template_data})

def cart_detail(request, cart_id):
    """Display details of a specific cart"""
    if not request.user.is_authenticated:
        return redirect('accounts.login')
    
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    template_data = {
        'title': f'Cart: {cart.name}',
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart.get_total(),
        'item_count': cart.get_item_count(),
    }
    return render(request, 'cart/cart_detail.html', {'template_data': template_data})

@login_required
def add(request, id):
    """Add movie to a specific cart"""
    movie = get_object_or_404(Movie, id=id)
    cart_id = request.POST.get('cart_id')
    quantity = int(request.POST.get('quantity', 1))
    
    if not cart_id:
        messages.error(request, 'Please select a cart.')
        return redirect('movies.show', id=id)
    
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    
    # Check if movie already exists in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        movie=movie,
        defaults={'quantity': quantity, 'price': movie.price}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'Added {movie.name} to {cart.name}')
    return redirect('cart.detail', cart_id=cart.id)

@login_required
def create_cart(request):
    """Create a new cart for the user"""
    if request.method == 'POST':
        cart_name = request.POST.get('cart_name', '').strip()
        
        if not cart_name:
            messages.error(request, 'Cart name is required.')
            return redirect('cart.index')
        
        # Check if user already has 3 carts
        user_cart_count = Cart.objects.filter(user=request.user).count()
        if user_cart_count >= 3:
            messages.error(request, 'You can only have 3 carts maximum.')
            return redirect('cart.index')
        
        # Check if cart name already exists for this user
        if Cart.objects.filter(user=request.user, name=cart_name).exists():
            messages.error(request, 'A cart with this name already exists.')
            return redirect('cart.index')
        
        cart = Cart.objects.create(user=request.user, name=cart_name)
        messages.success(request, f'Cart "{cart_name}" created successfully!')
        return redirect('cart.detail', cart_id=cart.id)
    
    return redirect('cart.index')

@login_required
def update_item_quantity(request, cart_id, item_id):
    """Update quantity of an item in a cart"""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    new_quantity = int(request.POST.get('quantity', 1))
    
    if new_quantity <= 0:
        cart_item.delete()
        messages.success(request, f'Removed {cart_item.movie.name} from cart.')
    else:
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f'Updated quantity for {cart_item.movie.name}.')
    
    return redirect('cart.detail', cart_id=cart.id)

@login_required
def remove_item(request, cart_id, item_id):
    """Remove an item from a cart"""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    movie_name = cart_item.movie.name
    cart_item.delete()
    
    messages.success(request, f'Removed {movie_name} from cart.')
    return redirect('cart.detail', cart_id=cart.id)

@login_required
def clear_cart(request, cart_id):
    """Clear all items from a specific cart"""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    CartItem.objects.filter(cart=cart).delete()
    
    messages.success(request, f'Cleared all items from {cart.name}.')
    return redirect('cart.detail', cart_id=cart.id)

@login_required
def delete_cart(request, cart_id):
    """Delete an entire cart"""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_name = cart.name
    cart.delete()
    
    messages.success(request, f'Deleted cart "{cart_name}".')
    return redirect('cart.index')

@login_required
def purchase(request, cart_id):
    """Purchase items from a specific cart"""
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items.exists():
        messages.error(request, 'Cart is empty.')
        return redirect('cart.detail', cart_id=cart.id)
    
    cart_total = cart.get_total()
    
    with transaction.atomic():
        # Create order
        order = Order.objects.create(
            user=request.user,
            total=cart_total,
            cart=cart
        )
        
        # Create order items
        for cart_item in cart_items:
            Item.objects.create(
                movie=cart_item.movie,
                price=cart_item.price,
                order=order,
                quantity=cart_item.quantity
            )
        
        # Clear the cart
        cart_items.delete()
    
    template_data = {
        'title': 'Purchase confirmation',
        'order_id': order.id,
        'cart_name': cart.name,
        'total': cart_total,
    }
    return render(request, 'cart/purchase.html', {'template_data': template_data})