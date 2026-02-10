from django.contrib import admin

from .models import *

admin.site.register([User, EmailVerify, WishList,
                     Cart, Order, OrderItem])