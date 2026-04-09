from django.contrib import admin
from .models import User, Payment

admin.site.register(User)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'razorpay_order_id', 'created_at']
    list_filter  = ['status', 'plan']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
