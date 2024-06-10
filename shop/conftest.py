import pytest

from shop.models import Brand


@pytest.fixture
def brands():
    lst = []
    for i in range(5):
        lst.append(Brand.objects.create(name='i'))
    return lst