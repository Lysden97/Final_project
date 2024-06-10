import pytest
from django.contrib.auth.models import User

from shop.models import Brand, Product, Comment, Cart, CartProduct, Order


@pytest.fixture
def brands():
    lst = []
    for i in range(5):
        lst.append(Brand.objects.create(name='i'))
    return lst


@pytest.fixture
def user():
    return User.objects.create_user(username='user')

@pytest.fixture
def other_user():
    return User.objects.create_user(username='other_user')


@pytest.fixture
def superuser():
    return User.objects.create_superuser(username='superuser')


@pytest.fixture
def brand():
    return Brand.objects.create(name='i')


@pytest.fixture
def products(brand):
    lst = []
    for i in range(5):
        lst.append(Product.objects.create(name='i', brand=brand, price=10.29, for_whom=2, description='text'))
    return lst


@pytest.fixture
def comments(products, user):
    lst = []
    for i in range(5):
        lst.append(Comment.objects.create(product=products[0], user=user, text='comment', date='2020-01-01'))
    return lst

@pytest.fixture
def cart(user, products):
    c = Cart.objects.create(user=user)
    for product in products:
        CartProduct.objects.create(cart=c, product=product, quantity=2)
    return c

@pytest.fixture
def create_order(user):
    return Order.objects.create(user=user)