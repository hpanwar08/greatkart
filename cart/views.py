from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404

from cart.models import Cart, CartItem
from store.models import Product


def _get_session_id(request: HttpRequest):
    session_id = request.session.session_key
    if not session_id:
        session_id = request.session.create()
    return session_id


def add_to_cart(request: HttpRequest, product_id: int):
    product = Product.objects.get(id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_get_session_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_get_session_id(request))
        cart.save()

    try:
        cart_item = CartItem.objects.get(cart_id=cart.id, product=product)
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(cart_id=cart.id, product=product, quantity=0)

    cart_item.quantity += 1
    cart_item.save()

    return redirect('cart:cart')


def remove_from_cart(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, cart_id=_get_session_id(request))
    cart_item = CartItem.objects.get(cart_id=cart.id, product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart:cart')


def remove_cart_item(request: HttpRequest, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, cart_id=_get_session_id(request))
    cart_item = get_object_or_404(CartItem, cart_id=cart.id, product=product)

    cart_item.delete()

    return redirect('cart:cart')


def cart(request: HttpRequest):
    quantity = 0
    total = 0
    grand_total = 0
    tax = 0
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_get_session_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total += (item.quantity * item.product.price)
            quantity += item.quantity
        tax = (2 * total) / 100  # 2% tax , move to db
        grand_total = total + tax
    except ObjectDoesNotExist as ode:
        print(ode)

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'store/cart.html', context=context)
