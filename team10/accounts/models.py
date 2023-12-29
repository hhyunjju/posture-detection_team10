from django.db import models
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.signals import user_logged_in


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    nickname = models.CharField(max_length=30, blank = True, default = '')
    email = models.EmailField(blank=True)
    
    def save(self, *args, **kwargs):
        #닉네임이 비어있으면 사용자의 이름으로 채운다
        if not self.nickname:
            self.nickname = self.user.username
        super().save(*args, **kwargs)

class UserSession(models.Model): #사용자의 세션 정보 저장
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

#중복 로그인 방지  #사용자 로그인시 호출되는 함수
def block_duplicate_login(sender, request, user, **kwargs):
    login_user_list = UserSession.objects.filter(user=user)
    for user_session in login_user_list: #동일한 사용자에 대해 기존에 저장된 모든 세션 기록 조회
        session = SessionStore(user_session.session_key)
        # session.delete()
        session['blocked'] = True #동일한 사용자의 기존 세션을 찾아, 해당 세션에 'blocked'키 저장
        session.save() #새로운 세션 기록 저장
        
    session_key = request.session.session_key #ㅐ로운 세션 기록 생성
    UserSession.objects.create(user=user, session_key = session_key) #UserSession기록에 추가

 #사용자가 로그인할 때마다 함수 호출되도록 user_logged_in 신호에 함수 연결
 # 다른 창이나 탭에서 동일한 브라우저를 사용하는 경우, 일반적으로 동일한 세션을 공유
user_logged_in.connect(block_duplicate_login)

from allauth.socialaccount.signals import social_account_updated
from django.dispatch import receiver
from .models import Profile
# 네이버 로그인을 통해 가입할 때 필요한 정보를 Profile 모델에 저장
@receiver(social_account_updated)
def save_naver_profile(request, sociallogin, **kwargs):
    # 네이버 로그인의 경우에만 처리
    if sociallogin.account.provider == 'naver':
        user = sociallogin.user
        data = sociallogin.account.extra_data
        profile, created = Profile.objects.get_or_create(user=user)
        profile.nickname = data.get('nickname', '')
        profile.phone_number = data.get('phone_number', '')
        profile.email = data.get('email', '')
        profile.save()
