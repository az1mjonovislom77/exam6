from django.urls import path
from .views import (
    IndexView, ProductListView, ProductDetailView, CategoryProductsView, place_order, LikeProductView,
    CustomerListView, CustomerCreateView, CustomerUpdateView, CustomerDeleteView, CustomerDetailView
)
from django.conf import settings
from django.conf.urls.static import static


app_name = "myapp"

urlpatterns = [
                  path('', IndexView.as_view(), name='index'),
                  path('products/', ProductListView.as_view(), name='product_list'),
                  path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
                  path('category/<slug:slug>/', CategoryProductsView.as_view(), name='category_products'),
                  path('order/<slug:slug>/', place_order, name='place_order'),
                  path('like/<slug:slug>/', LikeProductView.as_view(), name='like_product'),
                  path('customers/', CustomerListView.as_view(), name='customer_table'),
                  path('add-customer/', CustomerCreateView.as_view(), name='add_customer'),
                  path('edit-customer/<int:pk>/', CustomerUpdateView.as_view(), name='edit_customer'),
                  path('delete-customer/<int:pk>/', CustomerDeleteView.as_view(), name='delete_customer'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
