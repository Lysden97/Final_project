from django.contrib.auth.models import User
from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    CHOICES = (
        (1, 'Unisex'),
        (2, 'Product for women'),
        (3, 'Product for men')
    )
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    for_whom = models.IntegerField(choices=CHOICES, default=1)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} {self.brand} {self.price} {self.for_whom} {self.description}'


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Cart(models.Model):
    products = models.ManyToManyField(Product, through='CartProduct')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def total(self):
        total = 0
        for cb in self.cartproduct_set.all():
            total += cb.total()
        return total

    def get_total(self):
        return f'{self.total():.2f}'


class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total(self):
        return self.quantity * self.product.price


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    date = models.DateTimeField(auto_now_add=True)

    def total(self):
        total = 0
        for cb in self.orderproduct_set.all():
            total += cb.total()
        return f'{total:.2f}'


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total(self):
        return self.quantity * self.product.price
