import os
import random
import json
from django.db.models.signals import pre_save, pre_delete
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from core.settings import BASE_DIR
from .models import Customer, Category, Order, Product

User = get_user_model()


@receiver(pre_save, sender=Customer)
def generate_vat_number(sender, instance, **kwargs):
    if not instance.vat_number:
        while True:
            new_vat = str(random.randint(100000000, 999999999))
            if not Customer.objects.filter(vat_number=new_vat).exists():
                instance.vat_number = new_vat
                break


def notify_superusers(subject, message):
    superusers = User.objects.filter(is_superuser=True).values_list('email', flat=True)
    email_list = list(superusers)

    if email_list:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=email_list,
            fail_silently=False,
        )


@receiver(post_save, sender=Customer)
def customer_updated(sender, instance, created, **kwargs):
    if created:
        subject = 'Yangi customer qo‘shildi'
        message = f'Yangi customer qo‘shildi:\n\nIsm: {instance.name}\nEmail: {instance.email}\nTelefon: {instance.phone}'
    else:
        subject = 'Customer ma’lumotlari yangilandi'
        message = f'Customer ma’lumotlari yangilandi:\n\nIsm: {instance.name}\nEmail: {instance.email}\nTelefon: {instance.phone}'

    notify_superusers(subject, message)


@receiver(post_delete, sender=Customer)
def customer_deleted(sender, instance, **kwargs):
    subject = 'Customer o‘chirildi'
    message = f'Customer o‘chirildi:\n\nIsm: {instance.name}\nEmail: {instance.email}\nTelefon: {instance.phone}'

    notify_superusers(subject, message)


@receiver(post_save, sender=Product)
def product_updated(sender, instance, created, **kwargs):
    if created:
        subject = 'Yangi product qo‘shildi'
        message = f'Yangi product qo‘shildi:\n\nNomi: {instance.name}\nNarxi: {instance.price}\nMiqdori: {instance.quantity}'
    else:
        subject = 'Product yangilandi'
        message = f'Product ma’lumotlari yangilandi:\n\nNomi: {instance.name}\nNarxi: {instance.price}\nMiqdori: {instance.quantity}'

    notify_superusers(subject, message)


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    subject = 'Product o‘chirildi'
    message = f'Product o‘chirildi:\n\nNomi: {instance.name}\nNarxi: {instance.price}\nMiqdori: {instance.quantity}'
    notify_superusers(subject, message)


@receiver(post_save, sender=Order)
def order_updated(sender, instance, created, **kwargs):
    if created:
        subject = 'Yangi buyurtma qabul qilindi'
        message = f"Yangi buyurtma:\n\nMijoz: {instance.customer_name}\nTelefon: {instance.customer_phone}\nProduct: {instance.product.name if instance.product else 'Noma’lum'}\nMiqdori: {instance.quantity}"
    else:
        subject = 'Buyurtma yangilandi'
        message = f"Buyurtma ma’lumotlari yangilandi:\n\nMijoz: {instance.customer_name}\nTelefon: {instance.customer_phone}\nProduct: {instance.product.name if instance.product else 'Noma’lum'}\nMiqdori: {instance.quantity}"

    notify_superusers(subject, message)


@receiver(post_delete, sender=Order)
def order_deleted(sender, instance, **kwargs):
    subject = 'Buyurtma o‘chirildi'
    message = f"Buyurtma o‘chirildi:\n\nMijoz: {instance.customer_name}\nTelefon: {instance.customer_phone}\nProduct: {instance.product.name if instance.product else 'Noma’lum'}\nMiqdori: {instance.quantity}"
    notify_superusers(subject, message)


@receiver(post_save, sender=Category)
def category_updated(sender, instance, created, **kwargs):
    if created:
        subject = 'Yangi kategoriya qo‘shildi'
        message = f'Kategoriya qo‘shildi:\n\nNomi: {instance.title}'
    else:
        subject = 'Kategoriya yangilandi'
        message = f'Kategoriya ma’lumotlari yangilandi:\n\nNomi: {instance.title}'

    notify_superusers(subject, message)


@receiver(post_delete, sender=Category)
def category_deleted(sender, instance, **kwargs):
    subject = 'Kategoriya o‘chirildi'
    message = f'Kategoriya o‘chirildi:\n\nNomi: {instance.title}'
    notify_superusers(subject, message)


data = Product


@receiver(pre_delete, sender=Product)
def save_data_before_deleted(sender, instance, **kwargs):
    data = {
        'name': instance.name,
        'description': instance.description,
        'price': float(instance.price),
        'image': str(instance.image.url),
        'discount': instance.discount,
        'quantity': instance.quantity,
        'category': instance.category.id
    }
    file_path = os.path.join(BASE_DIR, 'myapp', 'backup', 'product_backup.json')
    if os.path.exists(file_path):
        with open(file_path) as f:
            try:
                product_data = json.load(f)
            except json.JSONDecodeError:
                product_data = []
    else:
        product_data = []
    product_data.append(data)
    with open(file_path, 'w') as f:
        json.dump(product_data, f, indent=4)

    print('Product successfully saved')
