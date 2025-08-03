# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Customer
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_profile_and_customer(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            username=instance.username,
            email=instance.email,
            name=instance.first_name
        )

        Customer.objects.create(
            user=instance,
            name=instance.first_name,
            email=instance.email
        )

        try:
            send_mail(
                subject='Welcome to DevSearch',
                message='We are glad you are here!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            print('Email failed:', str(e))


@receiver(post_save, sender=Profile)
def update_user_from_profile(sender, instance, created, **kwargs):
    if not created:
        user = instance.user
        user.first_name = instance.name
        user.username = instance.username
        user.email = instance.email
        user.save()


@receiver(post_delete, sender=Profile)
def delete_user_when_profile_deleted(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except Exception as e:
        print('User delete failed:', str(e))
