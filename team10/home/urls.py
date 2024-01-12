# home/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views
from .views import home_view
from django.contrib import admin

app_name = 'home'

urlpatterns = [
    path('', home_view, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('intro/', views.intro, name='intro'),
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('brd/', include('brd.urls')),
    path('service/', include('service.urls')),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('data-policy/', views.data_policy, name='data_policy'),
]