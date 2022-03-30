import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect

from category.models import Category
from order.models import OrderItem
from store.forms import ReviewRatingForm
from store.models import Product, ReviewRating

logger = logging.getLogger(__file__)


def store(request: HttpRequest, category_slug: str = None):
    products = None
    product_count = None

    if category_slug:
        category = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True).order_by('id')
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        product_count = products.count()

    paginator = Paginator(products, 6)
    page_num = request.GET.get('page')
    paged_products = paginator.get_page(page_num)

    context = {'products': paged_products, 'product_count': product_count}

    return render(request, 'store/store.html', context)


def product_detail(request: HttpRequest, category_slug, product_slug):
    product = None
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # is_product_in_cart = CartItem.objects.filter(cart__cart_id=_get_session_id(request), product=product).exists()
    except Product.DoesNotExist as ex:
        raise ex

    order_item = None
    if request.user.is_authenticated:
        try:
            order_item = OrderItem.objects.filter(user=request.user, product=product).exists()
        except OrderItem.DoesNotExist as ex:
            logger.exception(ex)

    reviews = ReviewRating.objects.filter(product=product, status=True)

    context = {
        'product': product,
        # 'is_product_in_cart': is_product_in_cart,
        'order_item': order_item,
        'reviews': reviews
    }

    return render(request, 'store/product_detail.html', context)


def search_products(request: HttpRequest):
    keyword = request.GET.get('keyword')
    products = Product.objects.order_by('-created_at').filter(
        Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request, 'store/store.html', context)


@login_required
def submit_review(request: HttpRequest, product_id: int):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewRatingForm(request.POST, instance=review)
            form.save()
            messages.success(request, "Thank you for your review")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            logger.warning('Review does not exists')
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.user = request.user
                data.product_id = product_id
                data.save()
                messages.success(request, "Thank you for your review")
                return redirect(url)
