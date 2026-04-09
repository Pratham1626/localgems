from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    email      = models.EmailField(unique=True)
    firstname  = models.CharField(max_length=50, blank=True, null=True)
    lastname   = models.CharField(max_length=50, blank=True, null=True)
    gender_choice = (('male','Male'),('female','Female'),('other','Other'))
    gender     = models.CharField(max_length=10, choices=gender_choice, blank=True, null=True)
    mobile     = models.CharField(max_length=15, blank=True, null=True)

    role_choice = (('owner','owner'),('user','user'))
    role = models.CharField(max_length=10, choices=role_choice, default='user')

    PLAN_CHOICES = (('free','Free'),('pro','Pro'),('elite','Elite'))
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    is_admin   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending',  'Pending'),
        ('success',  'Success'),
        ('failed',   'Failed'),
    )
    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan              = models.CharField(max_length=10)
    amount            = models.PositiveIntegerField(help_text='Amount in paise')
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature  = models.CharField(max_length=200, blank=True)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} | {self.plan} | {self.status}"
