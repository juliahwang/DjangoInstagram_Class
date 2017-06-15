from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.

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
        # 요청받은 POST데이터에서 username, password키가 가진 값들을
        # username, password 변수에 할당(문자열)
        username = request.POST['username']
        password = request.POST['password']
        # authenticate함수를 사용해서 User객체를 얻어 user에 할당
        # 인증에 실패할 경우 user변수에는 None이 할당됨
        user = authenticate(request, username=username, password=password)
        # user변수가 None이 아닐경우 (정상적으로 인증되어 User객체를 얻은 경우)
        if user is not None:
            # 장고의 session을 활용해 이번 request와 user데이터로 login()한 후
            # post_list페이지로 리다이렉트한다.
            django_login(request, user)
            return redirect('post:post_list')
        # user가 인증에 실패한 경우 다음 HttpResponse를 반환
        else:
            return HttpResponse('Login Invalid!')
    # request.method가 GET이면 login 템플릿을 보여준다.
    else:
        # 만약 이미 로그인된 상태일 경우에는 post_list로 redirect
        # 아닐경우 login.html을 render해서 리턴
        if request.user.is_authenticated:
            return redirect('post:post_list')
        return render(request, 'member/login.html')


def logout(request):
    # 로그아웃되면 post_list로 redirect
    django_logout(request)
    return redirect('post:post_list')
