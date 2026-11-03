from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('users/',      include('users.urls',     namespace='users')),
    path('nutrition/',  include('nutrition.urls',  namespace='nutrition')),
    path('',            include('chatbot.urls',    namespace='chatbot')),
    path('dashboard/',  RedirectView.as_view(url='/nutrition/dashboard/')),
]