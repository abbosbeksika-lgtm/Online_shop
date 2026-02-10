from decimal import Decimal
from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from products.models import Product



class User(AbstractUser):
    USER_ROLES = (
        ("admin","Admin"),
        ("user","User"),
        ("seller","Seller")
    )
    phone = models.CharField(max_length=13, null=True, blank=True)
    image = models.ImageField(upload_to="user_images/",null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    role = models.CharField(max_length=10, choices=USER_ROLES, default="user")

    def __str__(self):
        return self.username

class EmailVerify(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emailcode', null=True, blank=True)
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        expiry_time = self.created_at + timedelta(minutes=2)
        return timezone.now() < expiry_time

    def str(self):
        return f"{self.email} - {self.code}"


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlists')


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.quantity = int(self.quantity)
        if self.product.precent > 0:
            self.total_price = self.product.discount_price * self.quantity
        else:
            self.total_price = self.product.price * self.quantity

        super().save(*args, **kwargs)

    def __str__(self):
        return self.product.title


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order.user.username} -> {self.product.title}"
