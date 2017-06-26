from pprint import pprint
import requests
from django.contrib import messages
from django.contrib.auth import login as django_login, logout as django_logout, get_user_model
from django.shortcuts import render, redirect

from config import settings
from ..forms import LoginForm, SignupForm

# Create your views here.
User = get_user_model()

__all__ = (
    'login',
    'logout',
    'signup',
    'facebook_login',
)


def login(request):
    # member/login.html 생성
    #   username, password, button이 있는 html
    #   POST 요청이 올 경유 좌측 코드를 기반으로 로그인 완료 후 post_list로 이동
    #   실패할 경우 HttpResponse로 'Login invalid!' 띄워주기

    # /member/login/으로 접근시 이 view로 오도록 설정
    # config/urls.py에 member/urls.py를 include
    #   member/urls.py에 app_name으로 namespace지정

    # POST요청이 왔을 경우
    if request.method == 'POST':
        ### Form클래스 미사용시
        # 요청받은 POST데이터에서 username, password키가 가진 값들을
        # username, password 변수에 할당(문자열)
        # username = request.POST['username']
        # password = request.POST['password']
        # authenticate함수를 사용해서 User객체를 얻어 user에 할당
        # 인증에 실패할 경우 user변수에는 None이 할당됨
        # user = authenticate(request, username=username, password=password)
        # user변수가 None이 아닐경우 (정상적으로 인증되어 User객체를 얻은 경우)
        # if user is not None:
        # 장고의 session을 활용해 이번 request와 user데이터로 login()한 후
        # post_list페이지로 리다이렉트한다.
        # django_login(request, user)
        # return redirect('post:post_list_original')
        # user가 인증에 실패한 경우 다음 HttpResponse를 반환

        ### Form클래스 사용시
        #   Bound form 생성
        form = LoginForm(data=request.POST)
        # Bound form의 유효성검사를 하여 받아온 데이터가 조건에 부합하는지 검사. 유효할 경우 True반환
        if form.is_valid():
            # 데이터가 유효할 경우 cleaned_data에 데이터가 들어간다.
            # 그 데이터를 빼내와서 user객체에 user의 value값을 할당.
            user = form.cleaned_data['user']
            django_login(request, user)
            # url에서 GET요청을 할 때 로그인 후에도 원래 있던 페이지주소(next값)를 기억하여
            # 그 쪽으로 보내준다. next_값이 없을 경우에는 원래 랜딩페이지인 post_list로 간다.
            next_ = request.GET.get('next')
            if next_:
                return redirect(next_)
            return redirect('post:post_list')

    # request.method가 GET이면 login 템플릿을 보여준다.
    else:
        # 만약 이미 로그인된 상태일 경우에는 post_list로 redirect
        if request.user.is_authenticated:
            return redirect('post:post_list')
        # 아닐 경우 login.html을 render해서 리턴
        # LoginForm 인스턴스를 생성해서 context에 넘김
        form = LoginForm()
    context = {
        'form': form,
    }
    # render시 context에는 LoginForm 클래스형 form 객체가 포함되어 있다.
    # return render(request, 'member/login.html', context)
    return render(request, 'member/login.html', context)


def logout(request):
    # 로그아웃되면 post_list로 redirect
    django_logout(request)
    return redirect('post:post_list')


def signup(request):
    # member/signup.html을 사용
    #   username, password1, password2를 받아
    #   이미 유저가 존재하는지 검사
    #   password1, 2가 일치하는지 검사
    #   각각의 경우를 검사해서 틀릴경우 오류메세지 턴
    #   가입에 성공시 로그인시키고 post_list로 리다이렉트
    ### 폼을 사용하지 않는 경우
    # if request.method == 'POST':
    #     username = request.POST['username']
    #     password1 = request.POST['password1']
    #     password2 = request.POST['password2']
    #     if User.objects.filter(username=username).exists():
    #         return HttpResponse('Username already exists')
    #     elif password1 != password2:
    #         return HttpResponse('You should type the exact same password!')
    #     # 위 두 경우가 아닌 경우 유저를 생성
    #     user = User.objects.create_user(
    #         username=username,
    #         password=password1,
    #     )
    #     django_login(request, user)
    #     return redirect('post:post_list_original')
    # else:
    #     return render(request, 'member/signup.html')

    ### form 사용시
    if request.method == 'POST':
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.create_user()
            django_login(request, user)
            return redirect('post:post_list')
        else:
            context = {
                'form': form,
            }
            return render(request, 'member/signup.html', context)
    # GET요청이 올 때는 form을 보여주고 clean_username()에서 정의한
    # ValidationError까지(발생할 경우) 포함하여 출력해줄 수 있다.
    form = SignupForm()
    context = {
        'form': form,
    }
    return render(request, 'member/signup.html', context)


def facebook_login(request):
    # facebook_login view가 처음 호출될 때
    #   유저가 Facebook login dialog에서 로그인 후, 페이스북에서 우리 서비스(Consumer)쪽으로
    #   GET 파라미터를 이용해 'code'값을 전달해줌 (전달받는 주소는 위의 uri_redirect)
    # code= 값이 있을 때만 로그인을 허용
    code = request.GET.get('code')
    app_access_token = '{}|{}'.format(
        settings.FACEBOOK_APP_ID,
        settings.FACEBOOK_SECRET_CODE
    )

    # Exception을 상속받아 CustomException을 생성
    class GetAccessTokenException(Exception):
        def __init__(self, *args, **kwargs):
            error_dict = args[0]['data']['error']
            self.code = error_dict['code']
            self.message = error_dict['message']
            self.is_valid = error_dict['is_valid']
            self.scopes = error_dict['scopes']

    class DebugTokenException(Exception):
        def __init__(self, *args, **kwargs):
            error_dict = args[0]['data']['error']
            self.code = error_dict['code']
            self.message = error_dict['message']

    def add_message_and_redirect_referer():
        """
        페이스북 로그인 오류 메세지를 request에 추가하고 이전 페이지로 redirect
        :return: redirect
        """
        error_message_for_user = 'Facebook login error'
        messages.error(request, error_message_for_user)
        return redirect(request.META['HTTP_REFERER'])

    def get_access_token(code):
        """
        code를 받아 액세스토큰 교환 URL에 요청 이후 해당 액세스토큰을 반환
        오류 발생시 오류 메세지 리턴
        :param code:
        :return:
        """
        # facebook_login view가 처음 호출될 때 'code' request GET parameter를 받음
        # 액세스토큰의 코드교환할 url을 만들어준다.
        url_access_token = 'https://graph.facebook.com/v2.9/oauth/access_token'

        # 이전에 요청했던 redirect_uri와 같은 값을 만들어줌(access_token을 요청할 때 필요)
        redirect_uri = '{}://{}{}'.format(
            request.scheme,
            request.META['HTTP_HOST'],
            request.path,
        )
        # 액세스토큰의 코드 교환 - uri 생성을 위한 params
        url_access_token_params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': redirect_uri,
            'client_secret': settings.FACEBOOK_SECRET_CODE,
            'code': code,
        }
        # 해당 url에 get요청 후 결과(json형식)를 파이썬 object로 변환(result 변수)
        response = requests.get(url_access_token, params=url_access_token_params)
        # 액세스 토큰 출력해보기
        result = response.json()
        # 좀더 깨끗하게 갖고오는 pprint메서드 사용
        pprint(result)
        # {'access_token': 'EAAFGwwGAqT8BAND82fJLGNBAZAY9BMmiFL7zilPtTmZCZBBPFL5gEvHjkTGn4p9T3OGJ9A29oQrL6LW8EenN6GpirlWr7kYhZALVTFlQi0wkt8e8zzuiJyrCtH1u2UMdvh6ZB7jo1q2lDanZA9vdpFEZCRCOP1JviLjZAOUdEDpZCm67BbRRloOlB',
        #  'expires_in': 5179068,
        #  'token_type': 'bearer'}
        if 'access_token' in result:
            return result['access_token']
        elif 'error' in result:
            raise GetAccessTokenException(result)
        else:
            raise Exception('Unknown Error')

    def debug_token(token):
        url_debug_token = "https://graph.facebook.com/debug_token"
        url_debug_token_params = {
            'input_token': token,
            'access_token': app_access_token,
        }
        response = requests.get(url_debug_token, url_debug_token_params)
        result = response.json()
        if 'error' in result['data']:
            raise DebugTokenException(result)
        else:
            return result

    def get_user_info(user_id, token):
        url_user_info = 'https://graph.facebook.com/v2.9/{user_id}'.format(
            user_id=user_id
        )
        url_user_info_params = {
            'access_token': token,
            # 권한을 요청하지 않아도 오는 기본 정보
            # 반드시 scope 내용을 적어줘야한다.
            'fields': ','.join([
                'id',
                'name',
                'first_name',
                'last_name',
                'picture',
                'gender',
            ])
        }
        response = requests.get(url_user_info, params=url_user_info_params)
        result = response.json()
        print(result)

    # code 키값이 존재하지 않으면 로그인을 더이상 진행하지 않음.
    if not code:
        return add_message_and_redirect_referer()
    try:
        # 이 view에 GET parameter로 전달된 code를 사용해서 access_token을 받아옴
        # 성공시 access_token값을 가져옴
        # 실패시 GetAccessTokenException이 발생
        access_token = get_access_token(code)

        # 위에서 받아온 access_token을 이용해 debug_token을 요청
        # 성공시 토큰을 디버그한 결과 (user_id, scopes 등..)이 리턴
        # 실패시 DebugTokenException이 발생
        debug_result = debug_token(access_token)

        # debug_result에 있는 user_id값을 이용해서 GraphAPI에 유저정보를 요청
        user_info = get_user_info(user_id=debug_result['data']['user_id'], token=access_token)
        print('user_info : ', user_info)
    except GetAccessTokenException as e1:
        print('AccessToken Error code : ', e1.code)
        print('AccessToken Error msg : ', e1.message)
        return add_message_and_redirect_referer()
    except DebugTokenException as e2:
        print('Debug Error code : ', e2.code)
        print('Debug Error msg : ', e2.message)
        return add_message_and_redirect_referer()

