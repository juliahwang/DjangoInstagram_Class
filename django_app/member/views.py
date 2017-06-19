from django.contrib.auth import authenticate, login as django_login, logout as django_logout, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import LoginForm, SignupForm

# Create your views here.
User = get_user_model()


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
        # return redirect('post:post_list')
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
    #     return redirect('post:post_list')
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
