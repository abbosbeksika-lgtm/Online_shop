from django.urls import path
from .views import CheckoutView, OrderSuccessView, OrderListView

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', OrderSuccessView.as_view(), name='order_success'),
    path('my-orders/', OrderListView.as_view(), name='my_orders'),
]
