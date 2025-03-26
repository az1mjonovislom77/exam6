from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
import re

from .models import Category, Product, Customer, Order, Like
from .forms import CustomerForm


class IndexView(ListView):
    model = Product
    template_name = 'myapp/index.html'
    context_object_name = 'products'

    def get_queryset(self):
        search_query = self.request.GET.get('q', '')
        if search_query:
            return Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product-list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/product-details.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryProductsView(ListView):
    model = Product
    template_name = 'myapp/product-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        products = Product.objects.filter(category=category)
        filter_type = self.request.GET.get('filter', None)

        if filter_type == "new":
            return products.order_by('-created_at')
        elif filter_type == "likes":
            return products.order_by('-likes')
        elif filter_type == "expensive":
            return products.order_by('-price')
        elif filter_type == "cheap":
            return products.order_by('price')

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['slug'])
        return context


def place_order(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        quantity = request.POST.get('quantity', '')

        uzbekistan_phone_regex = re.compile(r'^\+998\d{9}$')
        if not uzbekistan_phone_regex.match(customer_phone):
            messages.error(request, 'Noto‘g‘ri telefon raqam! +998 XX XXX-XX-XX formatida kiriting')
            return redirect('myapp:product_detail', slug=product.slug)

        if not customer_name or not customer_phone or not quantity:
            messages.error(request, 'Iltimos, barcha maydonlarni to‘ldiring!')
            return redirect('myapp:product_detail', slug=product.slug)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Iltimos, musbat butun son kiriting!')
            return redirect('myapp:product_detail', slug=product.slug)

        if product.quantity < quantity:
            messages.error(request, f'Kechirasiz, faqat {product.quantity} ta mahsulot qolgan!')
            return redirect('myapp:product_detail', slug=product.slug)

        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            product=product,
            quantity=quantity
        )
        order.save()

        product.quantity -= quantity
        product.save()

        messages.success(request, 'Buyurtmangiz muvaffaqiyatli joylandi!')
        return redirect('myapp:index')

    context = {'product': product}
    return render(request, 'myapp/order.html', context)


class LikeProductView(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        user = request.user

        if Like.objects.filter(user=user, product=product).exists():
            messages.warning(request, 'Siz allaqachon bu mahsulotga layk bosgansiz!')
        else:
            Like.objects.create(user=user, product=product)
            product.likes += 1
            product.save()
            messages.success(request, 'Siz bu mahsulotga layk bosdingiz!')

        return redirect(request.META.get('HTTP_REFERER', 'myapp:index'))


class CustomerListView(ListView):
    model = Customer
    template_name = 'myapp/customers.html'
    context_object_name = 'customers'


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'myapp/customer_add.html'
    success_url = reverse_lazy('myapp:customer_table')


class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'myapp/customer_edit.html'
    success_url = reverse_lazy('myapp:customer_table')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        messages.success(self.request, 'Mijoz muvaffaqiyatli yangilandi!')
        return super().form_valid(form)


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'myapp/customers.html'
    success_url = reverse_lazy('myapp:customer_table')
    pk_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, pk=kwargs.get('pk'))
        messages.success(request, f"{customer.name} muvaffaqiyatli o‘chirildi!")
        return super().delete(request, *args, **kwargs)


def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'myapp/customer_details.html', {'customer': customer})