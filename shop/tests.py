from django.test import TestCase
import pytest
from django.test import Client
from django.urls import reverse

from shop.models import Product


def test_base_view():
    url = reverse('base')
    client = Client()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_brands_list(brands):
    url = reverse('brands_list')
    client = Client()
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['object_list'].count() == len(brands)
    for b in brands:
        assert b in response.context['object_list']


def test_add_brand_get():
    url = reverse('add_brand')
    client = Client()
    response = client.get(url)
    assert response.status_code == 302
    login_url = reverse('login')
    assert response.url == f'{login_url}?next={url}'


@pytest.mark.django_db
def test_add_brand_get_login(superuser, user):
    url = reverse('add_brand')
    client = Client()
    if client.force_login(superuser):
        response = client.get(url)
        assert response.status_code == 200
    else:
        client.force_login(user)
        response = client.post(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_add_brand_post_login(superuser, user):
    url = reverse('add_brand')
    client = Client()
    data = {
        'name': 'test',
    }
    if client.force_login(superuser):
        response = client.post(url, data)
        assert response.status_code == 302
    else:
        client.force_login(user)
        response = client.post(url, data)
        assert response.status_code == 403


@pytest.mark.django_db
def test_products_list(products):
    url = reverse('products_list')
    client = Client()
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['object_list'].count() == len(products)
    for p in products:
        assert p in response.context['object_list']


def test_add_product_get():
    url = reverse('add_product')
    client = Client()
    response = client.get(url)
    assert response.status_code == 302
    login_url = reverse('login')
    assert response.url == f'{login_url}?next={url}'


@pytest.mark.django_db
def test_add_product_get_login(superuser, user):
    url = reverse('add_product')
    client = Client()
    if client.force_login(superuser):
        response = client.get(url)
        assert response.status_code == 200
    else:
        client.force_login(user)
        response = client.post(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_add_product_post_login(superuser, brand):
    url = reverse('add_product')
    client = Client()
    client.force_login(superuser)
    data = {
        'name': 'test',
        'brand': brand.id,
        'price': 2.99,
        'for_whom': 1,
        'description': 'text',
    }
    response = client.post(url, data)
    assert response.status_code == 302

@pytest.mark.django_db
def test_detail_product_view(products):
    url = reverse('detail_product', args=(products[0].pk,))
    client = Client()
    response = client.get(url)
    assert response.status_code == 200
    product_context = response.context['object']
    assert product_context == products[0]

