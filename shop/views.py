from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView

from shop.forms import AddCommentForm
from shop.models import Brand, Product, Comment


class AddBrandView(PermissionRequiredMixin, CreateView):
    permission_required = ['shop.add_brand']

    model = Brand
    fields = '__all__'
    template_name = 'shop/form.html'
    success_url = reverse_lazy('add_brand')


class BrandsListView(ListView):
    model = Brand
    template_name = 'shop/brand_list.html'


class AddProductView(PermissionRequiredMixin, CreateView):
    permission_required = ['shop.add_product']

    model = Product
    fields = '__all__'
    template_name = 'shop/form.html'
    success_url = reverse_lazy('add_product')


class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'


class DetailProductView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddCommentForm()
        return context


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, product_pk):
        form = AddCommentForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(pk=product_pk)
            comment = form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()
            return redirect('detail_product', product_pk)
        return render(request, 'shop/product_detail.html', {'form': form})


class UpdateCommentView(UserPassesTestMixin, View):
    def test_func(self):
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        return self.request.user == comment.user

    def get(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        form = AddCommentForm(instance=comment)
        return render(request, 'shop/form.html', {'form': form})

    def post(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        form = AddCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('detail_product', comment.product.pk)
        return render(request, 'shop/form.html', {'form': form})
