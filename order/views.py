from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.


def place_order(request:HttpRequest):
    return render(request, '')
