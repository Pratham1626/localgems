from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import role_required
from .models import Gem, OpenCall, Application
from .forms import GemProfileForm, OpenCallForm, ApplicationForm
from core.models import User


# ── Public Pages ──────────────────────────────────────────────────────────────

def artBoardView(request):
    """Browse all artists"""
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    gems = Gem.objects.all()
    if category:
        gems = gems.filter(category=category)
    if city:
        gems = gems.filter(city__icontains=city)
    categories = Gem.CATEGORY_CHOICES
    return render(request, 'gems/public/art_board.html', {
        'gems': gems,
        'categories': categories,
        'selected_category': category,
        'selected_city': city,
    })


def artistProfileView(request, pk):
    """Public artist profile page"""
    gem = get_object_or_404(Gem, pk=pk)
    return render(request, 'gems/public/artist_profile.html', {'gem': gem})


def openCallsView(request):
    """Browse open calls"""
    calls = OpenCall.objects.exclude(status='closed').order_by('-created_at')
    return render(request, 'gems/public/open_calls.html', {'calls': calls})


def howItWorksView(request):
    return render(request, 'gems/public/how_it_works.html')


def artistSpotlightView(request):
    featured = Gem.objects.filter(is_featured=True)[:6]
    if not featured:
        featured = Gem.objects.all()[:6]
    return render(request, 'gems/public/artist_spotlight.html', {'gems': featured})


def localEventsView(request):
    calls = OpenCall.objects.filter(status='open').order_by('-created_at')[:10]
    return render(request, 'gems/public/local_events.html', {'calls': calls})


def successStoriesView(request):
    return render(request, 'gems/public/success_stories.html')


def helpCenterView(request):
    return render(request, 'gems/public/help_center.html')


def privacyView(request):
    return render(request, 'gems/public/privacy.html')


def termsView(request):
    return render(request, 'gems/public/terms.html')


# ── Apply to Open Call ────────────────────────────────────────────────────────

@login_required(login_url='login')
def applyOpenCallView(request, pk):
    call = get_object_or_404(OpenCall, pk=pk)
    already_applied = Application.objects.filter(open_call=call, applicant=request.user).exists()
    if already_applied:
        messages.info(request, "You have already applied to this call.")
        return redirect('open_calls')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.open_call = call
            app.applicant = request.user
            app.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('open_calls')
    else:
        form = ApplicationForm()
    return render(request, 'gems/public/apply.html', {'form': form, 'call': call})


# ── Owner Dashboard ───────────────────────────────────────────────────────────

@role_required(allowed_roles=['owner'])
def ownerDashboardView(request):
    my_calls = OpenCall.objects.filter(posted_by=request.user).order_by('-created_at')
    total_applications = Application.objects.filter(open_call__posted_by=request.user).count()
    return render(request, 'gems/owner/owner_dashboard.html', {
        'my_calls': my_calls,
        'total_applications': total_applications,
    })


@role_required(allowed_roles=['owner'])
def createOpenCallView(request):
    if request.method == 'POST':
        form = OpenCallForm(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            call.posted_by = request.user
            call.save()
            messages.success(request, "Open call posted successfully!")
            return redirect('owner_dashboard')
    else:
        form = OpenCallForm()
    return render(request, 'gems/owner/create_open_call.html', {'form': form})


@role_required(allowed_roles=['owner'])
def viewApplicationsView(request, pk):
    call = get_object_or_404(OpenCall, pk=pk, posted_by=request.user)
    applications = call.applications.select_related('applicant').all()
    return render(request, 'gems/owner/view_applications.html', {
        'call': call,
        'applications': applications,
    })


# ── User Dashboard ────────────────────────────────────────────────────────────

@role_required(allowed_roles=['user'])
def userDashboardView(request):
    try:
        gem = request.user.gem_profile
    except Gem.DoesNotExist:
        gem = None
    my_applications = Application.objects.filter(applicant=request.user).select_related('open_call').order_by('-applied_at')
    return render(request, 'gems/user/user_dashboard.html', {
        'gem': gem,
        'my_applications': my_applications,
    })


@role_required(allowed_roles=['user'])
def editGemProfileView(request):
    try:
        gem = request.user.gem_profile
    except Gem.DoesNotExist:
        gem = None

    if request.method == 'POST':
        form = GemProfileForm(request.POST, instance=gem)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile updated!")
            return redirect('user_dashboard')
    else:
        form = GemProfileForm(instance=gem)
    return render(request, 'gems/user/edit_profile.html', {'form': form})
