from django.urls import path
from .views import CheckoutView, OrderSuccessView, OrderListView, OrderDetailView, OrderCancelView

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', OrderSuccessView.as_view(), name='order_success'),
    # path('my-orders/', OrderListView.as_view(), name='order_list'),
    path('my-orders/', OrderListView.as_view(), name='my_orders'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
]
