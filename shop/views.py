from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from shop.models import Brand


class AddBrand(PermissionRequiredMixin, CreateView):
    permission_required = ['shop.add_brand']

    model = Brand
    fields = '__all__'
    template_name = 'shop/form.html'
    success_url = reverse_lazy('add_brand')


class BrandsList(ListView):
    model = Brand
    template_name = 'shop/brand_list.html'
