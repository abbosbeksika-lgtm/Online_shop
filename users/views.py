from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from products.models import Category
from .models import *
from django.core.mail import get_connection
from .models import User, EmailVerify
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product
import random
from decimal import Decimal
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order
from django.contrib import messages


def generate_code():
    return ''.join([str(random.randint(0, 9)) for i in range(6)])

class RegisterView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'auth/register.html', {"error": "Passwords must match."})

        if User.objects.filter(email=email).exists():
            return render(request, 'auth/register.html', {"error": "Email already exists."})

        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {"error": "Username already exists."})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False,
        )

        if send_otp(user):
            request.session['temp_user_id'] = user.id
            return redirect('verify-otp')
        else:
            return render(request, 'auth/register.html', {'error': "Email yuborishda xato. Qayta urinib koring!"})


class VerifyPage(View):
    def get(self, request):
        return render(request, 'auth/verify_otp.html')

    def post(self, request):
        code = request.POST.get('code')
        user_id = request.session.get('temp_user_id')

        if not user_id:
            return redirect('register')

        try:
            email_obj = EmailVerify.objects.get(users_id=user_id, code=code)
            if email_obj.is_valid():
                user = email_obj.users
                user.is_active = True
                user.save()
                email_obj.delete()
                return redirect('login')
            else:
                return render(request, 'auth/verify_otp.html', {'error': 'Kod vaqti o‘tgan!'})
        except EmailVerify.DoesNotExist:
            return render(request, 'auth/verify_otp.html', {'error': 'Noto‘g‘ri kod!'})

class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'auth/login.html', {'error': 'Username yoki parol xato!'})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


def send_otp(user):
    code = generate_code()

    EmailVerify.objects.filter(users=user).delete()

    EmailVerify.objects.create(users=user, code=code)

    try:
        send_mail(
            'Tasdiqlash kodi',
            f'Sizning tasdiqlash kodingiz: {code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Email yuborishda xato: {e}")
        return False

class ResendOTPView(View):
    def get(self, request):
        user_id = request.session.get('temp_user_id')
        if not user_id:
            return redirect('register')

        try:
            user = User.objects.get(id=user_id)
            # EmailVerify.objects.filter(email=user.email).delete()
            if send_otp(user):
                return redirect('verify-otp')
            else:
                return render(request, 'auth/resend_otp.html', {
                    'error': 'Email yuborishda xatolik yuz berdi. Qayta urunib koring'
                })
        except User.DoesNotExist:
            return redirect('register')


@login_required(login_url='login')
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    quantity = request.POST.get("quantity", 1)
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        return redirect('home')

    total_price = sum(item.total_price for item in cart_items)
    balance = request.user.balance or Decimal('0.00')

    if balance < total_price:
        return render(request, 'cart_detail.html', {
            'cart_items': cart_items,
            'error': 'Balansda mablag‘ yetarli emas!'
        })

    with transaction.atomic():
        request.user.balance -= total_price
        request.user.save()

        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                product=item.product,
                order=order,
                quantity=item.quantity,
                price=item.product.discount_price if item.product.precent > 0 else item.product.price
            )

        cart_items.delete()

    return redirect('home')

class CartDetailView(View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        return render(request, 'cart_detail.html', {'cart_items': cart_items})


class SellerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'seller'


class SellerProductListView(LoginRequiredMixin, SellerRequiredMixin, View):
    def get(self, request):
        products = Product.objects.filter(seller=request.user)
        return render(request, 'products.html', {'products': products})


class ProductCreateView(LoginRequiredMixin, SellerRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'create.html', {
            "categories": categories,
        })

    def post(self, request):
        title = request.POST.get('title')
        brand = request.POST.get('brand')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        desc = request.POST.get('desc')
        category_id = request.POST.get('category')
        main_image = request.FILES.get('main_image')
        discount_price = request.POST.get('discount_price')
        precent = request.POST.get('precent')

        category_obj = None
        if category_id:
            category_obj = get_object_or_404(Category, id=category_id)

        Product.objects.create(
            seller=request.user,
            category=category_obj,
            title=title,
            brand=brand,
            price=price,
            discount_price=discount_price if discount_price else None,
            precent=precent if precent else None,
            stock=stock,
            desc=desc,
            main_image=main_image
        )

        return redirect('profile')



class ProductUpdateView(LoginRequiredMixin, View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id, seller=request.user)
        from products.models import Category
        categories = Category.objects.all()

        return render(request, 'update.html', {
            'product': product,
            'categories': categories
        })

    def post(self, request, id):
        product = get_object_or_404(Product, id=id, seller=request.user)
        product.title = request.POST.get('title')
        product.brand = request.POST.get('brand')
        product.stock = request.POST.get('stock')
        product.price = request.POST.get('price')
        product.precent = request.POST.get('precent') or 0
        product.desc = request.POST.get('desc')

        category_id = request.POST.get('category')
        if category_id:
            product.category_id = category_id

        if 'main_image' in request.FILES:
            product.main_image = request.FILES['main_image']

        if product.title:
            product.save()
            messages.success(request, "Mahsulot muvaffaqiyatli yangilandi.")
            return redirect('profile')
        else:
            from products.models import Category
            categories = Category.objects.all()
            return render(request, 'update.html', {
                'product': product,
                'categories': categories
            })

class ProductDeleteView(LoginRequiredMixin, View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id, seller=request.user)
        product.delete()
        messages.success(request, "Mahsulot o'chirildi.")
        return redirect('profile')

    def post(self, request, id):
        product = get_object_or_404(Product, id=id, seller=request.user)
        product.delete()
        messages.success(request, "Mahsulot muvaffaqiyatli o'chirildi.")
        return redirect('profile')


@login_required(login_url='login')
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    quantity = request.POST.get("quantity", 1)
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', 'home'))


class SellerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'seller'


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
        context = {
            'orders': user_orders
        }
        return render(request, 'auth/profile.html', context)

@login_required(login_url='login')
def add_item(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required(login_url='login')
def remove_item(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

@login_required(login_url='login')
def delete_from_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
    return redirect('cart_detail')


@login_required(login_url='login')
def add_item(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required(login_url='login')
def remove_item(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

@login_required(login_url='login')
def delete_from_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
    return redirect('cart_detail')


def index(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = WishList.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'index.html', {
        'products': products,
        'categories': categories,
        'user_wishlist_ids': user_wishlist_ids
    })


@login_required(login_url='login')
def toggle_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wish_item, created = WishList.objects.get_or_create(user=request.user, product=product)

    if not created:
        wish_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


class WishListView(LoginRequiredMixin, View):
    def get(self, request):
        wishlist = WishList.objects.filter(user=request.user)
        return render(request, 'wishlist.html', {'wishlist': wishlist})


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'auth/profile_update.html')

    def post(self, request):
        user = request.user
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.age = request.POST.get('age')

        age = request.POST.get('age')
        if age:
            user.age = age
        if request.FILES.get('image'):
            user.image = request.FILES.get('image')

        user.save()
        return redirect('profile')