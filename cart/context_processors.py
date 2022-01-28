from django.http import HttpRequest

from cart.models import CartItem
from cart.views import _get_session_id


def cart_count(request: HttpRequest):
    cart_quantity_count = 0
    if 'admin' in request.path:
        return {}

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(buyer=request.user)
    else:
        cart_items = CartItem.objects.filter(cart__cart_id=_get_session_id(request))

    for item in cart_items:
        cart_quantity_count += item.quantity

    return {'cart_quantity_count': cart_quantity_count}
