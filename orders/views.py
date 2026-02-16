from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Cart
from orders.models import Order, OrderItem
from django.contrib import messages
from django.db import transaction


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
        order = Order.objects.create(user=request.user, total_price=total_price)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()
        return redirect('order_success')

class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'order_success.html')

class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'order_list.html', {'orders': orders})


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        items = OrderItem.objects.filter(order=order)

        context = {
            'order': order,
            'items': items
        }
        return render(request, 'orders_detail.html', context)


class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)

        if order.status == 'pending' and not order.is_paid:
            with transaction.atomic():
                items = order.items.all() if hasattr(order, 'items') else order.orderitem_set.all()
                for item in items:
                    item.product.stock += item.quantity
                    item.product.save()

                order.status = 'canceled'
                order.save()
                messages.success(request, "Buyurtma bekor qilindi va mahsulotlar omborga qaytdi.")
        else:
            messages.error(request, "Bu buyurtmani bekor qilib bo'lmaydi.")

        return redirect('order_detail', pk=pk)