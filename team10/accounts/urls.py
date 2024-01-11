from django.contrib import admin
from django.urls import path, reverse_lazy, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import *

app_name = 'accounts'

urlpatterns = [
    # path('idFind/', views.idFind, name='idFind'),
    # path('passwordRecovery/', views.passwordRecovery, name='passwordRecovery'),
    # 추가적인 URL 설정을 필요에 따라 작성하세요.
    path('login/', auth_views.LoginView.as_view(), name='login'),  # 로그인 URL 설정
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # 회원가입 URL 설정
    path('signup/', views.signup, name='signup'),
    path("profile", views.profile, name='profile'),
    path("password/", views.MyPasswordChangeView.as_view(), #success_url을 view에 작성하는 것으로 바꿈
         name="password_change"),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path('update/', views.update, name="profile_update"),
]