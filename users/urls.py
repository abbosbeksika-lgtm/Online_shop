from django.urls import path
from . import views
from .views import toggle_wishlist, WishListView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-otp/', views.VerifyPage.as_view(), name='verify-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/detail/', views.CartDetailView.as_view(), name='cart_detail'),
    path('seller/products/', views.SellerProductListView.as_view(), name='seller_product'),
    path('edit/product/<int:id>', views.ProductUpdateView.as_view(), name='edit_product'),
    path('add/product/', views.ProductCreateView.as_view(), name='add_product'),
    path('delete/product/<int:id>', views.ProductDeleteView.as_view(), name='delete_product'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('cart/add-item/<int:id>/', views.add_item, name='add_item'),
    path('cart/remove-item/<int:id>/', views.remove_item, name='remove_item'),
    path('cart/delete/<int:id>/', views.delete_from_cart, name='delete_from_cart'),
    path('wishlist/', WishListView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:id>/', toggle_wishlist, name='toggle_wishlist'),
]
