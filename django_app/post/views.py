from http.client import HTTPResponse
from django.contrib.auth import get_user_model
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import loader
from django.urls import reverse

from post.models import Post

# 자동으로 장고에서 인증에 사용하는 User모델클래스를 리턴
User = get_user_model()


def index(request):
    # Hello, world!를 출력하는 index함수를 만든다.
    return HTTPResponse('Hello, world!')


def post_list(request):
    # 모든 Post목록을 'post'라는 key로 context에 담아 return render처리
    posts = Post.objects.all()
    context = {
        'posts': posts
    }
    return render(
        request,
        'post/post_list.html',
        context=context,
    )


def post_detail(request, post_pk):
    # Model(DB)에서 post_pk에 해당하는 Post객체를 가져와 변수에 할당
    # ModelManager의 get 메서드를 통해 단 한 개의 객체만 가져온다.
    #   https://docs.djangoproject.com/en/1.11/ref/models/querysets/#get

    post = get_object_or_404(Post, pk=post_pk)
    # 가져오는 과정에서 예외처리하기
    #   - get()은 오브젝트가 없거나(DoesNotExist)
    #   - 여러 개의 오브젝트가 반환(MultipleObjectsReturns)될 때 에러가 난다

    # try:
    #     post = Post.objects.get(pk=post_pk)
    # except Post.DoesNotExist as e:
        # 1. 404에러를 띄워준다.
        # return HttpResponseNotFound('Post Not Found. detail: {}'.format(e))

        # 2. post_list view로 돌아간다.
        # 2-1. redirect를 사용
        #   https://docs.djangoproject.com/en/1.11/topics/http/shortcuts/#redirect
        # return redirect('post:post_list')
        # 301 : redirect 코드를 돌려줄 때 가는 페이지
        # redirect는 HttpResponseRedirect와 달리 모델, 뷰페이지를 가지고 페이지를 렌더링
        # 2-2. HttpResponseRedirect
        #   https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponseRedirect
        # 템플릿에서 reverse함수로 url을 조합, 함수를 써주는 것과 위의 redirect()는 결국 같은 기능을 한다.
        # url = reverse('post:post_list')
        # return HttpResponseRedirect(url)

    # request에 대해 response를 돌려줄 때는 HttpResponse나 render함수 사용
    # template을 사용할 경우 render함수를 사용한다
    # render함수는...
    #   django.template.loader.get_template함수와
    #   django.http.HttpResponse함수를 축약해 놓은 shortcut

    # ! 이 뷰에서는 render를 사용하지 않고 전체 과정(loader, HttpResponse)을 기술
    # Django가 템플릿을 검색할 수 있는 모든 디렉토리를 순회하며
    # 인자로 주어진 문자열 값과 일치하는 템플릿이 있는지 확인후
    # 템플릿을 template에 리턴 (django.template.backends.django.Template 클래스형 객체)
    # get_template() 메서드
    #   https://docs.djangoproject.com/en/1.11/topics/templates/#django.template.loader.get_template
    # template = loader.get_template('post/post_detail.html')
    # dict형 변수 context의 'post'키에 post(Post객체) 할당
    context = {
        # context로 전달될 dictionary의 key값이 템플릿에서 사용가능한 변수명이 된다.
        'post': post,
    }
    # template에 인자로 주어진 context, request를 render함수로 string을 받아온다.
    # rendered_string = template.render(request=request, context=context)
    # return HTTPResponse(rendered_string)

    # render를 사용하면 위의 과정을 함축하여 사용함과 동시에 post_detail.html으로 연결해준다.
    return render(request, 'post/post_detail.html', context=context)


def post_create(request):
    # POST요청을 받아 Post객체를 생성 후 post_list페이지로 redirect
    context = {
    }
    # post/post_create.html을 렌더하여 리턴.
    if request.method == 'GET':
        return render(request, 'post/post_create.html', context=context)
    else:
        # return HttpResponse('Post request')
        # 가져온 파일을 ImageField에 넣도록 설정
        # 'file'은 POST요청시 input[type='file']이 가진 name 속성
        photo = request.FILES['file']
        # get_user_model을 이용해서 얻은 User클래스(Django에서 인증에 사용하는 유저모델)에서 임의 유저 한명 가져오기
        author = User.objects.first()
        # 새로 post 생성
        post = Post.objects.create(author=author, photo=photo)

        # POST 요청시 name이 'comment'인 input에서 전달된 값을 가져옴
        # dic.get() : 딕셔너리 내장함수로 값을 가져온다
        comment_string = request.POST.get('comment', '')
        # 빈 문자열 ''이나 None 모두 False로 평가되므로
        # if not 으로 댓글로 쓸 내용 또는 comment키가 전달되지 않았음을 검사 가능
        if comment_string:
            # 댓글로 사용할 문자열이 전달된 경우 위에서 생성한 post객체에 연결되는 Comment객체를 생성해준다.
            post.comment_set.create(
                # 임의의 user를 사용하므로 나중에 실제 로그인된 사용자로 바꿔주어야함
                author=author,
                content=comment_string,
            )
            # 역참조로 가져온 RelatedManager를 사용하지 않을 경우엔 아래와 같이 작업함
            # Comment.objects.create(
            #     post=post,
            #     author=author,
            #     content=comment_string,
            # )
        return redirect('post:post_detail', post_pk=post.pk)


def post_modify(request, post_pk):
    pass
    # 수정
    # post = Post.objects.get(pk=post_pk)
    # if request.method == 'GET':
    #     context = {
    #         'photo': post.photo,
    #     }
    #     return render(request, 'post/post_modify.html', context)
    # else:
    #     photo = request.FILES['file']
    #     post.photo = photo
    #     post.save()
    #     return redirect('post:post_detail', post_pk=post.pk)


def post_delete(request, post_pk):
    if request.method == "POST":
        post = Post.objects.get(pk=post_pk)
        post.delete()
        return redirect('post:post_list')
    return HTTPResponse('you have no authority to delete')
    # post_pk에 해당하는 Post에 대한 delete요청만을 받음
    # 처리완료 후에는 post_list페이지로 redirect


def post_anyway(request):
    return redirect('post:post_anyway')


def comment_create(request, post_pk):
    # POST 요청을 받아 Comment객체를 생성 후 post_detail페이지로 redirect
    pass


def comment_modify(request, post_pk):
    # 코멘트 수정
    pass
