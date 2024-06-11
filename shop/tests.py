import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from shop.forms import AddCommentForm
from shop.models import Comment, CartProduct, Cart, Order, Brand, Product


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


@pytest.mark.django_db
def test_create_order(cart):
    url = reverse('create_order')
    client = Client()
    client.force_login(cart.user)
    product_count = cart.products.count()
    response = client.post(url)
    assert response.status_code == 302
    redirect_url = reverse('order_list')
    assert response.url == redirect_url
    o = Order.objects.get(user=cart.user)
    assert o.products.count() == product_count


@pytest.mark.django_db
def test_create_order_not_logged_in(cart):
    url = reverse('create_order')
    client = Client()
    response = client.post(url)
    login = reverse('login')
    redirect_url = f"{login}?next={url}"
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.django_db
def test_order_list_logged_in(user, create_order):
    client = Client()
    client.force_login(user)
    response = client.get(reverse('order_list'))
    assert response.status_code == 200
    orders = response.context['object_list']
    assert len(orders) == 1
    assert orders[0].user == user


@pytest.mark.django_db
def test_order_list_not_logged_in():
    client = Client()
    response = client.get(reverse('order_list'))
    assert response.status_code == 302
    assert 'login' in response.url


@pytest.mark.django_db
def test_order_detail_logged_in(user, create_order):
    client = Client()
    client.force_login(user)
    order = create_order
    response = client.get(reverse('order_detail', args=(order.pk,)))
    assert response.status_code == 200
    assert response.context['object'] == order


@pytest.mark.django_db
def test_order_detail_not_logged_in(create_order):
    client = Client()
    order = create_order
    response = client.get(reverse('order_detail', args=(order.pk,)))
    assert response.status_code == 302
    assert 'login' in response.url


@pytest.mark.django_db
def test_product_search_view_with_query(create_product):
    client = Client()
    response = client.get(reverse('product_search'), {'q': create_product.name})
    assert response.status_code == 200
    assert 'products' in response.context
    assert len(response.context['products']) == 1
    assert response.context['products'][0].name == 'Laptop'


@pytest.mark.django_db
def test_product_search_view_without_query():
    client = Client()
    response = client.get(reverse('product_search'))
    assert response.status_code == 200
    assert 'products' in response.context
    assert len(response.context['products']) == 0


@pytest.mark.django_db
def test_update_brand_get(superuser, brand):
    url = reverse('update_brand', args=(brand.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
    form = response.context['form']
    assert form.instance == brand


@pytest.mark.django_db
def test_update_brand_post(superuser, brand):
    url = reverse('update_brand', args=(brand.pk,))
    client = Client()
    client.force_login(superuser)
    data = {
        'name': 'Updated'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('brands_list')
    brand.refresh_from_db()
    assert brand.name == 'Updated'


@pytest.mark.django_db
def test_delete_brand_get(superuser, brand):
    url = reverse('delete_brand', args=(brand.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert any(template.name == 'shop/delete_form.html' for template in response.templates)


@pytest.mark.django_db
def test_delete_brand_post(superuser, brand):
    url = reverse('delete_brand', args=(brand.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('brands_list')
    assert not Brand.objects.filter(pk=brand.pk).exists()


@pytest.mark.django_db
def test_update_product_get(superuser, create_product):
    url = reverse('update_product', args=(create_product.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
    form = response.context['form']
    assert form.instance == create_product


@pytest.mark.django_db
def test_update_product_post(superuser, create_product):
    url = reverse('update_product', args=(create_product.pk,))
    client = Client()
    client.force_login(superuser)
    data = {
        'name': 'new_name',
        'price': 1200,
        'brand': create_product.brand.pk,
        'for_whom': create_product.for_whom,
        'description': create_product.description
    }
    response = client.post(url, data)
    assert response.status_code == 302
    updated_product = Product.objects.get(pk=create_product.pk)
    assert updated_product.name == 'new_name'
    assert updated_product.price == 1200


@pytest.mark.django_db
def test_delete_product_get(superuser, create_product):
    url = reverse('delete_product', args=(create_product.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert any(template.name == 'shop/delete_form.html' for template in response.templates)


@pytest.mark.django_db
def test_delete_product_post(superuser, create_product):
    url = reverse('delete_product', args=(create_product.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('products_list')
    assert not Product.objects.filter(pk=create_product.pk).exists()


@pytest.mark.django_db
def test_delete_order_get(superuser, create_order):
    url = reverse('delete_order', args=(create_order.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert any(template.name == 'shop/delete_form.html' for template in response.templates)


@pytest.mark.django_db
def test_delete_order_post(superuser, create_order):
    url = reverse('delete_order', args=(create_order.pk,))
    client = Client()
    client.force_login(superuser)
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('order_list')
    assert not Order.objects.filter(pk=create_order.pk).exists()