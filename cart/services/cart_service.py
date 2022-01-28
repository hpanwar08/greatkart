import logging

from django.http import HttpRequest

from cart.models import CartItem, Cart
from store.models import Product, Variation

logger = logging.getLogger(__file__)


def _get_session_id(request: HttpRequest):
    session_id = request.session.session_key
    if not session_id:
        session_id = request.session.create()
    return session_id


def add_item_to_cart(request, product_id):
    current_user = request.user

    product = Product.objects.get(id=product_id)
    product_variation = []

    for key, value in request.POST.items():
        try:

            variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                              variation_value__iexact=value)
            product_variation.append(variation)

        except Variation.DoesNotExist as e:
            print(e)
    print(product_variation)

    if current_user.is_authenticated:
        # get items by user and product and find out if same variation exists. If yes then increase count
        cart_items = CartItem.objects.filter(buyer=current_user, product=product).prefetch_related('variations')
        if cart_items.exists():
            item_found = False
            # iterate and find item of same variation
            for cart_item in cart_items:
                print(cart_item)
                print(list(cart_item.variations.all()))
                if product_variation == list(cart_item.variations.all()):
                    cart_item.quantity += 1
                    cart_item.save()
                    item_found = True
                    break

            if not item_found:
                new_cart_item = CartItem.objects.create(buyer=current_user, product=product, quantity=1)
                new_cart_item.variations.add(*product_variation)
                new_cart_item.save()

        else:
            new_cart_item = CartItem.objects.create(buyer=current_user, product=product, quantity=1)
            new_cart_item.variations.add(*product_variation)
            new_cart_item.save()
    else:
        # get item by cart id and product and find out if same variation exists. If yes then increase count
        try:
            cart = Cart.objects.get(cart_id=_get_session_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_get_session_id(request))

        cart_items = CartItem.objects.filter(cart=cart, product=product).prefetch_related('variations')

        if cart_items.exists():
            item_found = False
            # iterate and get existing variation
            for cart_item in cart_items:
                print(cart_item)
                print(list(cart_item.variations.all()))
                if product_variation == list(cart_item.variations.all()):
                    cart_item.quantity += 1
                    cart_item.save()
                    item_found = True
                    break

            if not item_found:
                new_cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)
                new_cart_item.variations.add(*product_variation)
                new_cart_item.save()

        else:
            new_cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)
            new_cart_item.variations.add(*product_variation)
            new_cart_item.save()
