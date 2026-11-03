from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/',       views.register_view,     name='register'),
    path('login/',          views.login_view,         name='login'),
    path('logout/',         views.logout_view,        name='logout'),
    path('profile/',        views.profile_setup_view, name='profile'),
    path('pricing/',        views.pricing_view,       name='pricing'),
    path('payment/',        views.payment_view,       name='payment'),
    path('cancel-premium/', views.cancel_premium,     name='cancel_premium'),
]
