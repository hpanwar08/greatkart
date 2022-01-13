from django.http import HttpRequest
from django.shortcuts import render

from category.models import Category
from store.models import Product


def store(request: HttpRequest, category_slug: str = None):
    products = None
    product_count = None

    if category_slug:
        category = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        product_count = products.count()

    context = {'products': products, 'product_count': product_count}

    return render(request, 'store/store.html', context)


def product_detail(request: HttpRequest, category_slug, product_slug):
    product = None
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Product.DoesNotExist as ex:
        raise ex

    context = {'product': product}

    return render(request, 'store/product_detail.html', context)
