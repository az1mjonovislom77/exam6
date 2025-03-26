from django.contrib import admin
from django.contrib.auth.admin import Group, UserAdmin
from django.utils.html import format_html
from myapp.models import Product, Category, Order, ProductImage, Customer, Attribute, AttributeValue, ProductAttribute
from users.models import CustomUser
from import_export import resources
from import_export.admin import ImportExportModelAdmin

admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'is_staff', 'is_active')
    search_fields = ('email',)
    list_filter = ('is_staff', 'is_active')
    ordering = ('-id',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


# Register your models here.

class ProductInline(admin.StackedInline):
    model = Product


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ('id', 'title')


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5


@admin.register(Product)
class ProductModelAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ['id', 'name', 'price', 'image_tag', ]
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'category')
    inlines = [ProductImageInline]

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:50px; max-height:50px"/>'.format(obj.image.url))

    image_tag.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'product')
    search_fields = ('customer_name', 'customer_phone', 'product__name')
    list_filter = ('created_at',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'billing_address', 'joined_date')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('billing_address',)
    readonly_fields = ('vat_number',)


admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(ProductAttribute)
