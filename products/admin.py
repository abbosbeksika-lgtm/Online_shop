from django.contrib import admin
from .models import Category, Product, ProductImage

admin.site.register([Category, Product, ProductImage])
