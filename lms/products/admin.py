from django.contrib import admin

# Register your models here.
from products.models import Product, Discount



admin.site.register(Product)
admin.site.register(Discount)