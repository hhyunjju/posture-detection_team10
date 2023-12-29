from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from .models import Profile

class SignupForm(AllauthSignupForm):
    phone_number = forms.CharField()
    nickname = forms.CharField(required=False)
    email = forms.EmailField()

    def signup(self, request, user):
        # User 객체가 이미 생성되었고, 여기에 추가 정보를 저장할 수 있습니다.
        user.email = self.cleaned_data['email']
        user.save()
        
        profile = Profile.objects.create(
            user=user,
            phone_number = self.cleaned_data['phone_number'],
            nickname = self.cleaned_data['nickname'],
            email=self.cleaned_data['email']
        )
        return user
    
# save 메서드를 오버라이드하여 사용자 객체를 생성한 후에 해당 사용자의 프로필을 생성합니다. 
# 이때, Profile 모델에 user, phone_number, address를 저장합니다.