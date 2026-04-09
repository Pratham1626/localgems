import razorpay
import hmac
import hashlib

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

from .forms import UserSignupForm, UserLoginForm
from .models import Payment


# ── Helpers ───────────────────────────────────────────────────────────────────

def _razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ── Home ──────────────────────────────────────────────────────────────────────

def homeView(request):
    from gems.models import Gem, OpenCall
    featured_gems = Gem.objects.filter(is_featured=True)[:3]
    if featured_gems.count() < 3:
        featured_gems = Gem.objects.all()[:3]
    open_calls = OpenCall.objects.exclude(status='closed').order_by('-created_at')[:3]
    return render(request, 'home.html', {
        'featured_gems': featured_gems,
        'open_calls':    open_calls,
        'categories':    Gem.CATEGORY_CHOICES,
    })


# ── Auth ──────────────────────────────────────────────────────────────────────

def logoutView(request):
    logout(request)
    return redirect('login')


def userLoginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user     = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('owner_dashboard' if user.role == 'owner' else 'user_dashboard')
            return render(request, 'core/login.html', {
                'form': form, 'error': 'Invalid email or password.'
            })
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})


# ── Pricing (Step 1) ──────────────────────────────────────────────────────────

def pricingView(request):
    """User picks a plan → stored in session → go to signup."""
    if request.method == 'POST':
        plan = request.POST.get('plan')
        if plan in ('free', 'pro', 'elite'):
            request.session['selected_plan'] = plan
            return redirect('signup')
    return render(request, 'core/pricing.html', {
        'prices': settings.PLAN_PRICES_DISPLAY,
    })


# ── Signup (Step 2) ───────────────────────────────────────────────────────────

def userSignupView(request):
    if 'selected_plan' not in request.session:
        return redirect('pricing')

    plan = request.session['selected_plan']

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user      = form.save(commit=False)
            user.plan = plan
            # Free plan → activate immediately
            if plan == 'free':
                user.save()
                request.session.pop('selected_plan', None)
                _send_welcome(user)
                messages.success(request, 'Account created! Please sign in.')
                return redirect('login')
            else:
                # Paid plan → save user first, then go to payment
                user.save()
                request.session['pending_user_id'] = user.pk
                request.session.pop('selected_plan', None)
                return redirect('payment_checkout')
        return render(request, 'core/signup.html', {'form': form, 'plan': plan})

    form = UserSignupForm()
    return render(request, 'core/signup.html', {'form': form, 'plan': plan})


def _send_welcome(user):
    from django.core.mail import send_mail
    try:
        send_mail(
            subject='Welcome to LocalGems',
            message=f'Thank you for joining LocalGems on the {user.plan.capitalize()} plan!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass


# ── Payment Checkout (Step 3 — paid plans only) ───────────────────────────────

def paymentCheckoutView(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('pricing')

    from .models import User
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('pricing')

    plan   = user.plan
    amount = settings.PLAN_PRICES.get(plan)
    if not amount:
        return redirect('pricing')

    rz_key = settings.RAZORPAY_KEY_ID
    rz_order_id = None
    razorpay_available = (
        rz_key and
        not rz_key.startswith('rzp_test_XXXX') and
        settings.RAZORPAY_KEY_SECRET and
        not settings.RAZORPAY_KEY_SECRET.startswith('XXXX')
    )

    if razorpay_available:
        try:
            client   = _razorpay_client()
            rz_order = client.order.create({
                'amount':          amount,
                'currency':        'INR',
                'payment_capture': 1,
                'notes':           {'plan': plan, 'user_id': str(user.pk)},
            })
            rz_order_id = rz_order['id']
            Payment.objects.create(
                user=user,
                plan=plan,
                amount=amount,
                razorpay_order_id=rz_order_id,
                status='pending',
            )
        except Exception:
            razorpay_available = False

    return render(request, 'core/payment_checkout.html', {
        'user':               user,
        'plan':               plan,
        'amount':             amount,
        'amount_display':     settings.PLAN_PRICES_DISPLAY[plan],
        'rz_order_id':        rz_order_id or '',
        'rz_key_id':          rz_key,
        'razorpay_available': razorpay_available,
    })


# ── Payment Callback (Razorpay POST after payment) ────────────────────────────

@csrf_exempt
def paymentCallbackView(request):
    if request.method != 'POST':
        return redirect('home')

    rz_payment_id = request.POST.get('razorpay_payment_id', '')
    rz_order_id   = request.POST.get('razorpay_order_id', '')
    rz_signature  = request.POST.get('razorpay_signature', '')

    try:
        payment = Payment.objects.get(razorpay_order_id=rz_order_id)
    except Payment.DoesNotExist:
        return HttpResponseBadRequest('Invalid order.')

    # Verify signature
    body      = f"{rz_order_id}|{rz_payment_id}"
    expected  = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()

    if hmac.compare_digest(expected, rz_signature):
        # Payment verified ✓
        payment.razorpay_payment_id = rz_payment_id
        payment.razorpay_signature  = rz_signature
        payment.status              = 'success'
        payment.save()

        # Activate user plan
        user = payment.user
        user.plan = payment.plan
        user.save()

        # Clear session
        request.session.pop('pending_user_id', None)

        _send_welcome(user)
        return redirect('payment_success')
    else:
        payment.status = 'failed'
        payment.save()
        return redirect('payment_failed')


# ── Success / Failed pages ────────────────────────────────────────────────────

def paymentMockConfirmView(request):
    """Dev-only: simulate a successful payment without real Razorpay keys."""
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return redirect('pricing')
    from .models import User
    try:
        user = User.objects.get(pk=user_id)
        user.save()
        request.session.pop('pending_user_id', None)
        _send_welcome(user)
    except User.DoesNotExist:
        pass
    return redirect('payment_success')


def paymentSuccessView(request):
    return render(request, 'core/payment_success.html')


def paymentFailedView(request):
    return render(request, 'core/payment_failed.html')
