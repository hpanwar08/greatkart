from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render

from cart.models import CartItem
from cart.views import _get_session_id
from category.models import Category
from store.models import Product


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
        is_product_in_cart = CartItem.objects.filter(cart__cart_id=_get_session_id(request), product=product).exists()
    except Product.DoesNotExist as ex:
        raise ex

    context = {
        'product': product,
        'is_product_in_cart': is_product_in_cart
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
