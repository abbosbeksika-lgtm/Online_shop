from django.shortcuts import render
from django.template.defaulttags import csrf_token
from django.views import View
from products.models import Category, Product
from users.models import Cart
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Product


class HomeView(View):
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.all().order_by('-id')[:4]

        cart_items = []
        total_price = 0
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
            total_price = sum(item.total_price for item in cart_items)

        return render(request, 'index.html', {
            'categories': categories,
            'products': products,
            'cart_items': cart_items,
            'total_price': total_price,
        })

class ProductsView(View):
    def get(self, request):
        products = Product.objects.all()
        categories = Category.objects.all()

        category_id = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')


        if category_id:
            products = products.filter(category_id=category_id)

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        return render(request, 'products.html', {
            "products": products,
            "categories": categories,
        })


class ProductDetailView(View):
    def get(self, request, id):
        product = Product.objects.get(id=id)
        images = product.images.all()

        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:3]

        return render(request, 'product_detail.html', {
            "product": product,
            "images": images,
            "related_products": related_products,
        })
