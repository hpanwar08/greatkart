import datetime
import json

import logging
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from cart.models import CartItem
from order.forms import OrderForm
from order.models import Order, Payment, OrderItem
from store.models import Product

logger = logging.getLogger(__file__)


@require_POST
@login_required
def place_order(request: HttpRequest):
    current_user = request.user
    cart_items = CartItem.objects.filter(buyer=current_user).prefetch_related('product')

    if cart_items.count() < 1:
        return redirect('store:store')

    form = OrderForm(request.POST)
    if form.is_valid():
        total = 0

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

        print(form.data)
        order = Order()
        order.user = current_user
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
        order.order_total = grand_total
        order.tax = tax
        order.ip = request.META.get('REMOTE_ADDR')
        order.save()

        order_number = datetime.date.today().strftime('%Y%m%d')
        order.order_number = order_number + str(order.id)
        order.save()

        context = {
            'order': order,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
            'cart_items': cart_items,
        }

        return render(request, 'order/payment.html', context)

    return redirect('cart:checkout')


@require_POST
@login_required
def payment(request: HttpRequest):
    body = json.loads(request.body)

    order = Order.objects.get(user=request.user, order_number=body['orderID'], is_ordered=False)

    payment = Payment(
        user=request.user,
        payment_id=body['transactionID'],
        payment_method=body['paymentMethod'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # move cart items to order item table
    cart_items = CartItem.objects.filter(buyer=request.user)
    for cart_item in cart_items:
        order_item = OrderItem()
        order_item.order = order
        order_item.payment = payment
        order_item.user = request.user
        order_item.product = cart_item.product
        order_item.quantity = cart_item.quantity
        order_item.product_price = cart_item.product.price
        order_item.ordered = True

        order_item.save()

        order_item = OrderItem.objects.get(id=order_item.id)
        order_item.variation.add(*cart_item.variations.all())
        order_item.save()

        product = Product.objects.get(id=cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()

    # remove cart
    cart_items.delete()

    # notify user
    email_subject = 'Thank you for your order'
    email_body = render_to_string('order/order_receive_email.html', {'user': request.user, 'order':order})

    email_message = EmailMessage(email_subject, email_body, to=[request.user.email])
    email_message.send()
    logger.info('Order email sent.')

    # display order number and transaction number
    data = {
        'orderID': order.order_number,
        'transactionID': payment.payment_id
    }

    return JsonResponse(data)


def order_complete(request: HttpRequest):
    context  ={}
    return render(request, 'order/order_complete.html', context)