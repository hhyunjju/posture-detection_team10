# home/views.py

from django.shortcuts import render

def home_view(request):
    # 필요한 로직
    return render(request, 'home/home.html')


def intro(request):
    return render(request, 'home/intro.html')

def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'home/terms_of_service.html')

def data_policy(request):
    return render(request, 'home/data_policy.html')