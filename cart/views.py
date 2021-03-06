from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404

from cart.models import Cart, CartItem
from cart.services import cart_service


def _get_session_id(request: HttpRequest):
    session_id = request.session.session_key
    if not session_id:
        session_id = request.session.create()
    return session_id


def add_to_cart(request: HttpRequest, product_id: int):
    cart_service.add_item_to_cart(request, product_id)

    return redirect('cart:cart')


def remove_from_cart(request: HttpRequest, cart_item_id: int):
    current_user = request.user

    if current_user.is_authenticated:
        cart_item = CartItem.objects.get(id=cart_item_id, buyer=current_user)
    else:
        cart = get_object_or_404(Cart, cart_id=_get_session_id(request))
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart:cart')


def remove_cart_item(request: HttpRequest, cart_item_id: int):
    current_user = request.user

    if current_user.is_authenticated:
        cart_item = CartItem.objects.get(id=cart_item_id, buyer=current_user)
    else:
        cart = get_object_or_404(Cart, cart_id=_get_session_id(request))
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

    cart_item.delete()

    return redirect('cart:cart')


def cart(request: HttpRequest):
    quantity = 0
    total = 0
    grand_total = 0
    tax = 0
    cart_items = None

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(buyer=request.user, is_active=True).prefetch_related('variations',
                                                                                                      'product')
        else:
            cart = Cart.objects.get(cart_id=_get_session_id(request))
            # reduced 30 queries to 9 with prefetch_related
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).prefetch_related('variations', 'product')

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


@login_required
def checkout(request: HttpRequest):
    quantity = 0
    total = 0
    grand_total = 0
    tax = 0
    cart_items = None

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(buyer=request.user, is_active=True).prefetch_related('variations',
                                                                                                      'product')
        else:
            cart = Cart.objects.get(cart_id=_get_session_id(request))
            # reduced 30 queries to 9 with prefetch_related
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).prefetch_related('variations', 'product')

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
    return render(request, 'store/checkout.html', context)
