from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Username and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('/dashboard/')

    return render(request, 'users/register.html')
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Username ya password galat hai.')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('/users/login/')


@login_required
def profile_setup_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        # Personal info — empty string ko None mein convert karo
        age = request.POST.get('age', '').strip()
        profile.age = int(age) if age else None

        profile.gender = request.POST.get('gender', '').strip()

        height = request.POST.get('height_cm', '').strip()
        profile.height_cm = float(height) if height else None

        weight = request.POST.get('weight_kg', '').strip()
        profile.weight_kg = float(weight) if weight else None

        target = request.POST.get('target_weight_kg', '').strip()
        profile.target_weight_kg = float(target) if target else None

        # Lifestyle
        profile.activity_level = request.POST.get('activity_level')
        profile.health_goal    = request.POST.get('health_goal')

        # Health conditions
        profile.has_diabetes      = 'has_diabetes'     in request.POST
        profile.has_hypertension  = 'has_hypertension' in request.POST
        profile.has_pcos          = 'has_pcos'          in request.POST
        profile.has_thyroid_issue = 'has_thyroid_issue' in request.POST

        # Preferences
        profile.language_preference = request.POST.get('language_preference', 'en')
        profile.daily_water_goal_ml = request.POST.get('daily_water_goal_ml', 2000)

        # First name
        first_name = request.POST.get('first_name', '').strip()
        if first_name:
            request.user.first_name = first_name
            request.user.save()

        profile.save()
        profile.refresh_calculations()

        messages.success(request, 'Profile updated successfully!')
        return redirect('/dashboard/')

    context = { 'profile': profile }
    return render(request, 'users/profile_setup.html', context)

@login_required
def payment_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'card')
        plan           = request.POST.get('plan', 'monthly')

        # Demo — activate premium instantly
        profile.is_premium        = True
        profile.premium_activated = timezone.now()
        profile.payment_method    = payment_method

        if plan == 'monthly':
            profile.premium_expires = timezone.now() + timedelta(days=30)
        elif plan == 'yearly':
            profile.premium_expires = timezone.now() + timedelta(days=365)

        profile.save()
        messages.success(request, '🎉 Welcome to NutriGenix Premium!')
        return redirect('/dashboard/')

    plan = request.GET.get('plan', 'monthly')
    context = { 'plan': plan, 'profile': profile }
    return render(request, 'users/payment.html', context)


@login_required
def cancel_premium(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.is_premium = False
        profile.save()
        messages.success(request, 'Premium cancelled successfully.')
    return redirect('/users/profile/')
def pricing_view(request):
    """Pricing page showing subscription plans"""
    return render(request, 'users/pricing.html')