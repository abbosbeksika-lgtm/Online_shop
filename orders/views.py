from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Cart
from .models import Order, OrderItem


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.total_price for item in cart_items)

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
        })

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('products')

        total_price = sum(item.total_price for item in cart_items)

        # 1️⃣ Order yaratish
        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        # 2️⃣ OrderItem yaratish
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # 3️⃣ Stock kamaytirish (professional)
            item.product.stock -= item.quantity
            item.product.save()

        # 4️⃣ Cartni tozalash
        cart_items.delete()

        return redirect('order_success')


class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order_success.html')


class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'order_list.html', {
            'orders': orders
        })
