from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    # 인스턴스를 만들 때 초기화 메서드가 호출된다.
    # 이를 통해 초기화함수의 인자 중 필요한 것만 오버라이드 해주고
    # 나머지 인자는 그대로 실행시킨다.
    # (이 경우 ':' 기본값을 없애려 함)
    def __init__(self, *args, **kwargs):
        # 딕셔너리의 내장함수 setdefault()를 사용하여
        # label_suffix가 없으면 ''로 만들고 출력해준다.
        kwargs.setdefault('label_suffix', '')
        # 그리고 자신의 원래 __init__을 실행해준다.
        super().__init__(*args, **kwargs)

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': '사용자 아이디를 입력하세요',
            }
        )
    )
    # widget은 필드의 속성을 알려주는 기능을 한다.
    # 기본 속성을 오버라이드할 경우에는 반드시 위젯 안에 새로 정의한다.
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': '비밀번호를 입력하세요',
            }
        )
    )

    # is_valid를 실행했을 때, Form내부의 모든 field들에 대한
    # 유효성 검증을 실행하는 메서드
    def clean(self):
        # clean()메서드를 실행한 기본 결과 dict를 가져온다.
        # 기본 clean()을 오버라이드할 것이므로 super()로 불러온다.
        cleaned_data = super().clean()
        # username, password를 가져와 로컬변수에 할당
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # username, password를 이용해 사용자 authenticate
        user = authenticate(
            username=username,
            password=password,
        )
        # 인증에 성공할 경우, Form의 cleaned_data의 'user'키에
        # 인증된 User객체를 할당
        if user is not None:
            # 폼에서는 로그인을 시키지 않는다(request가 필요)
            # 로그인은 뷰에서 해주는 것이 좋다.
            self.cleaned_data['user'] = user
        # 인증에 실패한 경우, is_valid()를 통과하지 못하도록
        # ValidationError를 발생시킨다.
        else:
            raise forms.ValidationError(
                'Login credentials not valid'
            )
        # clean()을 오버라이드 했으므로 기존 리턴값 적어준다.
        return self.cleaned_data
