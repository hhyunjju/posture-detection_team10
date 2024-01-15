from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Profile
from django.utils.translation import gettext_lazy as _

class SignupForm(UserCreationForm):
    phone_number = forms.CharField(help_text=_('(선택사항)'))
    nickname = forms.CharField(required=False, help_text=_('별명 미작성 시 username으로 대체됩니다'))
    email = forms.EmailField(help_text=_('이메일 주소를 입력해주세요'))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = 'password'
        self.fields['password2'].label = 'Re-enter password'

        self.fields['password1'].help_text = '최소 8자 이상, 개인 정보와 너무 유사하거나 일반적으로 사용되는 비밀번호, 숫자만으로 구성될 수 없습니다.'
        self.fields['password2'].help_text = '이전에 입력한 비밀번호를 다시 입력해주세요.'
    
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
        help_texts = {
            'username': _('150자 이하의 문자, 숫자 및 @/./+/-/_ 만 사용할 수 있습니다.'),
            'password1': _('비밀번호는 8자 이상이어야 하며, 개인 정보와 너무 유사하거나 일반적으로 사용되는 비밀번호, 숫자만으로 구성될 수 없습니다.'),
            'password2': _('이전에 입력한 비밀번호와 동일하게 다시 입력해주세요.'),
        }
        error_messages = {
            'username': {
                'max_length': _('이 사용자 이름은 너무 깁니다. 150자 이하로 해주세요.'),
                'required': _('사용자 이름을 입력해주세요.'),
            },
            'password1': {
                'required': _('비밀번호를 입력해주세요'),
                'password_too_short': _('비밀번호는 최소 8자 이상이어야 합니다.'),
                'password_too_common': _('비밀번호가 너무 일반적입니다.'),
                'password_numerical': _('비밀번호는 숫자만으로 이루어질 수 없습니다.'),
            },
            'password2': {
                'required': _('비밀번호 확인을 입력해주세요.'),
                'password_mismatch': _('비밀번호가 일치하지 않습니다.'),
            },
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.save()
        
        profile = Profile.objects.create(
            user=user,
            phone_number = self.cleaned_data['phone_number'],
            # address = self.cleaned_data['address'],
            nickname = self.cleaned_data['nickname'],
            email=self.cleaned_data['email']
        )
        return user
    
# save 메서드를 오버라이드하여 사용자 객체를 생성한 후에 해당 사용자의 프로필을 생성합니다. 
# 이때, Profile 모델에 user, phone_number, address를 저장합니다.

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields =['nickname', 'email', 'phone_number']
        
        