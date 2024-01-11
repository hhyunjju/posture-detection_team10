from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.conf import settings
from .models import Profile
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views import View
# 회원가입 뷰 작성

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_URL)
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form':form})

def profile(request):
    profile = get_object_or_404(Profile, user=request.user )
    return render(request, 'registration/profile.html', {'profile':profile})

class MyPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.info(self.request, '비밀번호 변경이 완료되었습니다')
        return super().form_valid(form)
    

def update(request):
    profile = get_object_or_404(Profile, user=request.user )
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance = profile)
        if form.is_valid():
            form.save()
            return redirect('/accounts/profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'registration/profile_update.html', {'form':form, 'profile':profile})
            
    
