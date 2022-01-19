from django.db import models
from django.urls import reverse
from django.utils import timezone

from category.models import Category


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    product_images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super().filter(variation_category='color', is_active=True)

    def sizes(self):
        return super().filter(variation_category='size', is_active=True)


variation_choices = (
    ('color', 'color'),
    ('size', 'size')
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category = models.CharField(max_length=200, choices=variation_choices)
    variation_value = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = VariationManager()

    class Meta:
        ordering = ('variation_category',)

    def __str__(self):
        return f"{self.variation_category} - {self.variation_value}"
