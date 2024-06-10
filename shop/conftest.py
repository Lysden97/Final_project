import pytest
from django.contrib.auth.models import User

from shop.models import Brand, Product


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