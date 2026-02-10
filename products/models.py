from django.db import models
from django.conf import settings
from decimal import Decimal

class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.title

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precent = models.IntegerField(null=True, blank=True, default=0)
    main_image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    desc = models.TextField()
    stock = models.IntegerField()

    def save(self, *args, **kwargs):
        current_price = Decimal(str(self.price))

        try:
            val = int(self.precent) if self.precent else 0
        except (ValueError, TypeError):
            val = 0

        if val > 0:
            current_precent = Decimal(str(val))
            self.discount_price = current_price - ((current_price / Decimal('100')) * current_precent)
            self.precent = val
        else:
            self.discount_price = current_price
            self.precent = 0

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.product.title

