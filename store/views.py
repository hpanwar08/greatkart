from django.http import HttpRequest
from django.shortcuts import render


def store(request: HttpRequest):
    return render(request, 'store/store.html', {})
