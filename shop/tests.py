from django.test import TestCase
import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from shop.forms import AddCommentForm
from shop.models import Comment, CartProduct, Cart


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


@pytest.mark.django_db
def test_add_comment_post(user, products):
    url = reverse('add_comment', args=(products[0].pk,))
    client = Client()
    client.force_login(user)
    data = {
        'text': 'comment',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Comment.objects.filter(product=products[0], user=user).exists()


@pytest.mark.django_db
def test_add_comment_not_logged_in(user, products):
    url = reverse('add_comment', args=(products[0].pk,))
    client = Client()
    data = {
        'text': 'comment',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))
    assert not Comment.objects.filter(product=products[0]).exists()


@pytest.mark.django_db
def test_update_comment_get(user, comments):
    url = reverse('update_comment', args=(comments[0].pk,))
    client = Client()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, AddCommentForm)
    assert form.instance == comments[0]


@pytest.mark.django_db
def test_update_comment_post(user, comments):
    url = reverse('update_comment', args=(comments[0].pk,))
    client = Client()
    client.force_login(user)
    data = {
        'text': 'Updated comment',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    comments[0].refresh_from_db()
    assert comments[0].text == 'Updated comment'


@pytest.mark.django_db
def test_update_comment_not_owner(other_user, comments):
    url = reverse('update_comment', args=(comments[0].pk,))
    client = Client()
    client.force_login(other_user)
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_comment_owner(user, comments):
    url = reverse('delete_comment', args=(comments[0].pk,))
    client = Client()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, 'shop/delete_form.html')
    response = client.post(url)
    assert response.status_code == 302
    assert not Comment.objects.filter(pk=comments[0].pk).exists()

@pytest.mark.django_db
def test_delete_comment_not_owner(other_user, comments):
    url = reverse('delete_comment', args=(comments[0].pk,))
    client = Client()
    client.force_login(other_user)
    response = client.get(url)
    assert response.status_code == 403
    assert Comment.objects.filter(pk=comments[0].pk).exists()

@pytest.mark.django_db
def test_add_to_cart(products, user):
    url = reverse('add_to_cart', args=(products[0].pk,))
    client = Client()
    client.force_login(user)
    response = client.post(url)
    redirect_url = reverse('products_list')
    assert response.status_code == 302
    assert response.url == redirect_url
    assert CartProduct.objects.get(product=products[0], quantity=1)

@pytest.mark.django_db
def test_add_to_cart_not_logged_in(products):
    url = reverse('add_to_cart', args=(products[0].pk,))
    client = Client()
    response = client.post(url)
    login = reverse('login')
    redirect_url = f"{login}?next={url}"
    assert response.status_code == 302
    assert response.url == redirect_url
    assert not CartProduct.objects.filter(pk=products[0].pk).exists()

@pytest.mark.django_db
def test_show_cart_view_logged_in(user):
    client = Client()
    client.force_login(user)
    cart, _ = Cart.objects.get_or_create(user=user)
    response = client.get(reverse('cart'))
    assert response.status_code == 200
    assert any(template.name == 'shop/cart.html' for template in response.templates)
    assert 'cart' in response.context
    assert response.context['cart'] == cart

@pytest.mark.django_db
def test_show_cart_not_logged_in():
    client = Client()
    response = client.get(reverse('cart'))
    assert response.status_code == 302
    assert 'login' in response.url