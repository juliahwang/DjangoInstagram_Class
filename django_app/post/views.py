from http.client import HTTPResponse

from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.template import loader

from member.models import User
from post.models import Post


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

    # post = get_object_or_404(Post, pk=post_pk)
    # 가져오는 과정에서 예외처리하기
    #   - get()은 오브젝트가 없거나(DoesNotExist)
    #   - 여러 개의 오브젝트가 반환(MultipleObjectsReturns)될 때 에러가 난다

    try:
        post = Post.objects.get(pk=post_pk)
    except Post.DoesNotExist as e:
        # 1. 404에러를 띄워준다.
        # return HttpResponseNotFound('Post Not Found. detail: {}'.format(e))

        # 2. post_list view로 돌아간다.
        # 2-1. redirect를 사용
        #   https://docs.djangoproject.com/en/1.11/topics/http/shortcuts/#redirect
        return redirect('post:post_list')
        # 301 : redirect 코드를 돌려줄 때 가는 페이지
        # redirect는 HttpResponseRedirect와 달리 모델, 뷰페이지를 가지고 페이지를 렌더링
        # 2-2. HttpResponseRedirect
        #   https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponseRedirect

    # request에 대해 response를 돌려줄 때는 HTTPResponse나 render함수 사용
    # template을 사용할 경우 render함수를 사용한다
    # render함수는...
    #   django.template.loader.get_template함수와
    #   django.http.HTTPResponse함수를 축약해 놓은 shortcut

    # ! 이 뷰에서는 render를 사용하지 않고 전체 과정(loader, HttpResponse)을 기술
    # Django가 템플릿을 검색할 수 있는 모든 디렉토리를 순회하며
    # 인자로 주어진 문자열 값과 일치하는 템플릿이 있는지 확인후
    # 템플릿을 template에 리턴 (django.template.backends.django.Template클래스형 객체)
    # get_template() 메서드
    #   https://docs.djangoproject.com/en/1.11/topics/templates/#django.template.loader.get_template
    template = loader.get_template('post/post_detail.html')
    # dict형 변수 context의 'post'키에 post(Post객체) 할당
    context = {
        # context로 전달될 dictionary의 key값이 템플릿에서 사용가능한 변수명이 된다.
        'post': post,
    }
    # template에 인자로 주어진 context, request를 render함수로 string을 받아온다.
    rendered_string = template.render(request=request, context=context)
    return HTTPResponse(rendered_string)

    # render를 사용하면 위의 과정을 함축하여 사용함과 동시에 post_detail.html으로 연결해준다.
    # return render(request, 'post/post_detail.html', context=context)


def post_create(request):
    # POST요청을 받아 Post객체를 생성 후 post_list페이지로 redirect
    context = {
    }
    if request.method == 'GET':
        return render(request, 'post/post_create.html', context=context)
    else:
        photo = request.FILES['photoupload']
        author = User.objects.first()
        Post.objects.create(author=author, photo=photo)
        return redirect('post:post_list')


def post_modify(request, post_pk):
    # 수정
    post = Post.objects.get(pk=post_pk)
    if request.method == 'GET':
        context = {
            'photo': post.photo.url,
        }
        return render(request, 'post/post_modify.html', context)
    else:
        post.photo = request.FILES['photoupload']
        post.author = User.objects.first()
        modified_post = post.save()
        context = {
            'post': modified_post,
        }
        return render(request, 'post/post_detail.html', context)


def post_delete(request, post_pk):
    # post_pk에 해당하는 Post에 대한 delete요청만을 받음
    # 처리완료 후에는 post_list페이지로 redirect
    pass


def comment_create(request, post_pk):
    # POST 요청을 받아 Comment객체를 생성 후 post_detail페이지로 redirect
    pass


def comment_modify(request, post_pk):
    # 코멘트 수정
    pass
