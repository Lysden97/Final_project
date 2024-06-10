from django.test import TestCase
import pytest
from django.test import Client
from django.urls import reverse


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