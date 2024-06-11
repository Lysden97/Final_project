from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, DeleteView

from shop.forms import AddCommentForm
from shop.models import Brand, Product, Comment, Cart, CartProduct, Order, OrderProduct


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = Product.objects.all()
        return context


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


class DeleteCommentView(UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'shop/delete_form.html'

    def get_success_url(self):
        return reverse_lazy('detail_product', args=(self.object.product.pk,))

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user


class AddProductToCartView(LoginRequiredMixin, View):
    def post(self, request, product_pk):
        product = Product.objects.get(pk=product_pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        try:
            cartItem = CartProduct.objects.get(product=product, cart=cart)
            cartItem.quantity += 1
            cartItem.save()
        except CartProduct.DoesNotExist:
            cart.products.add(product)
        return redirect('products_list')


class ShowCartView(LoginRequiredMixin, View):
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        return render(request, 'shop/cart.html', {'cart': cart})


class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        if created or not cart.cartproduct_set.all():
            return redirect('cart')
        order = Order.objects.create(user=request.user)
        for cart_product in cart.cartproduct_set.all():
            OrderProduct.objects.create(product=cart_product.product,
                                        order=order,
                                        quantity=cart_product.quantity)
        cart.cartproduct_set.all().delete()
        return redirect('order_list')

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shop/order_list.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'shop/order_detail.html'


class ProductSearchView(ListView):
    model = Product
    template_name = 'shop/product_search.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(name__icontains=query)
        else:
            return Product.objects.none()
