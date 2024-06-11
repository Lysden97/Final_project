import pytest
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_create_user_view_get():
    url = reverse('register')
    client = Client()
    response = client.get(url)
    assert response.status_code == 200
    assert 'accounts/create_user.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_user_view_post_success():
    url = reverse('register')
    client = Client()
    data = {
        'username': 'testuser',
        'password': 'password123',
        'password2': 'password123'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('base')
    assert User.objects.filter(username='testuser').exists()


@pytest.mark.django_db
def test_login_view_get():
    url = reverse('login')
    client = Client()
    response = client.get(url)
    assert response.status_code == 200
    assert 'accounts/login.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_login_view_post_success():
    url = reverse('login')
    user = User.objects.create_user(username='testuser', password='password123')
    client = Client()
    data = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('base')
    authenticated_user = authenticate(username='testuser', password='password123')
    assert authenticated_user is not None


@pytest.mark.django_db
def test_logout_view():
    User.objects.create_user(username='testuser', password='password123')
    client = Client()
    client.login(username='testuser', password='password123')
    response = client.get(reverse('base'))
    assert response.wsgi_request.user.is_authenticated
    url = reverse('logout')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('base')
    response = client.get(reverse('base'))
    assert not response.wsgi_request.user.is_authenticated
