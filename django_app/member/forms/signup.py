from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login as django_login

from member.models import User


class SignupForm(forms.Form):
    # SignupForm을 구성하고 해당 form을 view에서 사용하도록 설정
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': '특수문자 제외 10자리로 입력하세요',
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '특수문자 포함 10~12자리',
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '특수문자 포함 10~12자리',
            }
        )
    )

    def clean_username(self):
        # 폼을 사용하지 않을 때 만들어준 유효성검사를 clean_<필드명>()메서드로 정의.
        # if User.objects.filter(username=username).exists():
        #   return HttpResponse('Username already exists')
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "The Username you typed is already in use. "
                "Please type another username."
            )
        return username

    def clean_password2(self):
        # password2필드로 필드클린 메서드를 쓰는 이유는 password1이
        # 입력되어 있어야 하기 때문.
        # password1과 비교하여 같은지 비교
        # .get()을 사용하는 것이 좋다.
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        # password1과 password2가 존재하고 같지 않을 때
        if password1 and password2 and password2 != password1:
            raise forms.ValidationError(
                "Password2 should be identical to Password1."
            )
        return password2

    def create_user(self):
        # 자신의 cleaned_data를 사용해서 유저를 생성
        # username과 password1이 있다는 가정하에 사용하므로 get()을 사용하지 않는다.
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        return user
