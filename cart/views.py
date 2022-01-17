from django.http import HttpRequest
from django.shortcuts import render


def cart(request: HttpRequest):
    return render(request, 'store/cart.html')
