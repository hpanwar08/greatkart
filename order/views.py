from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
# Create your views here.
from django.views.decorators.http import require_POST

from cart.models import CartItem
from order.forms import OrderForm
from order.models import Order


@require_POST
@login_required
def place_order(request: HttpRequest):
    current_user = request.user
    cart_items = CartItem.objects.filter(buyer=current_user)

    if cart_items.count() < 1:
        return redirect('store:store')

    form = OrderForm(request.POST)
    if form.is_valid():
        print(form.data)
        order = Order()
        order.first_name = form.cleaned_data['first_name']
        order.last_name = form.cleaned_data['last_name']
        order.email = form.cleaned_data['email']
        order.phone = form.cleaned_data['phone']
        order.address_line_1 = form.cleaned_data['address_line_1']
        order.address_line_2 = form.cleaned_data['address_line_2']
        order.city = form.cleaned_data['city']
        order.state = form.cleaned_data['state']
        order.country = form.cleaned_data['country']
        order.order_note = form.cleaned_data['order_note']

        return HttpResponse('form valid')

    return HttpResponse('ok')
