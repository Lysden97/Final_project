"""
URL configuration for KsiegarniaS18 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from shop import views
from shop.views import ProductSearchView

urlpatterns = [
    path('add_brand/', views.AddBrandView.as_view(), name='add_brand'),
    path('brands_list', views.BrandsListView.as_view(), name='brands_list'),
    path('add_product/', views.AddProductView.as_view(), name='add_product'),
    path('products_list/', views.ProductListView.as_view(), name='products_list'),
    path('detail_product/<int:pk>', views.DetailProductView.as_view(), name='detail_product'),
    path('add_comment/<int:product_pk>', views.AddCommentView.as_view(), name='add_comment'),
    path('update_comment/<int:pk>', views.UpdateCommentView.as_view(), name='update_comment'),
    path('delete_comment/<int:pk>', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('add_to_cart/<int:product_pk>', views.AddProductToCartView.as_view(), name='add_to_cart'),
    path('cart/', views.ShowCartView.as_view(), name='cart'),
    path('create_order/', views.CreateOrderView.as_view(), name='create_order'),
    path('order_list/', views.OrderListView.as_view(), name='order_list'),
    path('order_detail/<int:pk>', views.OrderDetailView.as_view(), name='order_detail'),
    path('product_search/', ProductSearchView.as_view(), name='product_search'),
]
