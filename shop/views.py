from django.shortcuts import render, HttpResponse, redirect, \
    get_object_or_404, reverse
from django.contrib import messages
from .models import Product, Order, LineItem, CartItem
from .forms import CartForm, CheckoutForm, ProductForm,AddToCartForm
from . import cart
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    all_products = Product.objects.all()
    return render(request, "shop/shop-index.html", {
                                    'all_products': all_products,
                                    })
def userindex(request):
    current_user = request.user
    all_products = Product.objects.filter(user_id=current_user.id)
    return render(request, "shop/shop-index.html", {
                                    'all_products': all_products,
                                    })

@user_passes_test(lambda u: u.is_creator)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, 'Your product has been listed!')
    else:
        form = ProductForm()
    return render(request, 'shop/create_product.html', {'form': form})

    '''if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            files = request.FILES.getlist('image')
            name = form.cleaned_data.get('name')
            price = form.cleaned_data.get('price')
            slug = form.cleaned_data.get('slug')
            description = form.cleaned_data.get('description')

            for file in files:
                file_instance = ProductForm(file=file, user=user)
                file_instance.save()
                files_objs.append(file_instance)
            

            product = Product(name=name, price=price, slug=slug, description=description, user=user)
            product.content.set(files_objs)
            product.save()
            messages.success(request, 'Your product has been created!')

    else:
        form = ProductForm()

    context = {
        'form': form,
    }
    return render(request, 'shop/newproduct.html', context)
'''

def show_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.user = request.user
            cart_item.cart_id = request.session.session_key
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect('cart')

    form = CartForm(request, initial={'product_id': product})
    return render(request, 'shop/product_detail.html', {
                                            'product': product,
                                            'form': form,
                                            })


from django.contrib.auth.decorators import login_required

@login_required
def show_cart(request):
    # Get the current user
    user = request.user

    # Get all cart items for the current user
    cart_items = CartItem.objects.filter(user=user)

    # Calculate the total cost of all cart items
    cart_total = sum([item.total_cost() for item in cart_items])

    # Render the cart template with the cart items and total cost
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })

def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_cost = sum(item.total_cost() for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_cost': total_cost})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.user = request.user
            cart_item.cart_id = request.session.session_key
            cart_item.product = product
            cart_item.price = product.price
            cart_item.save()
            return redirect('cart')
    else:
        form = AddToCartForm()
    
    return render(request, 'shop/add_to_cart.html', {'form': form, 'product': product})

'''def add_to_cart(request):
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cart_item = form.save(commit=False)
            cart_item.user = request.user
            cart_item.cart_id = request.session.session_key
            cart_item.price = cart_item.product.price
            cart_item.save()
            return redirect('cart')
    else:
        form = AddToCartForm()
    return render(request, 'shop/add_to_cart.html', {'form': form})'''

'''def show_cart(request):

    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            cart.update_item(request)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)

    cart_items = cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    return render(request, 'shop/cart.html', {
                                            'cart_items': cart_items,
                                            'cart_subtotal': cart_subtotal,
                                            })
'''

def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            o = Order(
                name = cleaned_data.get('name'),
                email = cleaned_data.get('email'),
                postal_code = cleaned_data.get('postal_code'),
                address = cleaned_data.get('address'),
            )
            o.save()

            all_items = cart.get_all_cart_items(request)
            for cart_item in all_items:
                li = LineItem(
                    product_id = cart_item.product_id,
                    price = cart_item.price,
                    quantity = cart_item.quantity,
                    order_id = o.id
                )

                li.save()

            cart.clear(request)

            request.session['order_id'] = o.id

            messages.add_message(request, messages.INFO, 'Order Placed!')
            return redirect('checkout')


    else:
        form = CheckoutForm()
        return render(request, 'shop/checkout.html', {'form': form})
    
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, 'Product removed from cart.')
    else:
        messages.error(request, 'You are not authorized to remove this product from the cart.')
    
    return redirect('cart')
