from django.urls import path
from . import views

urlpatterns = [
    path('',                views.homeView,             name='home'),
    path('pricing/',        views.pricingView,           name='pricing'),
    path('signup/',         views.userSignupView,        name='signup'),
    path('login/',          views.userLoginView,         name='login'),
    path('logout/',         views.logoutView,            name='logout'),
    path('payment/',        views.paymentCheckoutView,   name='payment_checkout'),
    path('payment/callback/', views.paymentCallbackView, name='payment_callback'),
    path('payment/mock-confirm/', views.paymentMockConfirmView, name='payment_mock_confirm'),
    path('payment/success/', views.paymentSuccessView,   name='payment_success'),
    path('payment/failed/',  views.paymentFailedView,    name='payment_failed'),
]
