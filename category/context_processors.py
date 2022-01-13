from django.http import HttpRequest

from category.models import Category


def category_processor(request: HttpRequest):
    links = Category.objects.all()
    return dict(links=links)
