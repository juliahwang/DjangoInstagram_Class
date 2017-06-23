from http.client import HTTPResponse

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from post.decorators import post_owner
from post.forms import CommentForm
from post.forms import PostForm
from post.models import Post, Tag

__all__ = (
    'post_list_original',
    'post_list',
    'post_create',
    'post_detail',
    'post_modify',
    'post_delete',
    'post_like_toggle',
    'hashtag_post_list',
)

# Create your views here.
# 자동으로 장고에서 인증에 사용하는 User모델클래스를 리턴
User = get_user_model()


def index(request):
    # Hello, world!를 출력하는 index함수를 만든다.
    return HTTPResponse('Hello, world!')


def post_list_original(request):
    # 모든 Post목록을 'post'라는 key로 context에 담아 return render처리
    posts = Post.objects.all()
    context = {
        'posts': posts,
        # post마다 CommentForm을 1개씩 가지도록 전달.
        'comment_form': CommentForm(),
    }
    return render(
        request,
        'post/post_list.html',
        context=context,
    )


# 페이지네이션
def post_list(request):
    # 아직 평가되지 않은 전체 쿼리셋 들고오기
    all_posts = Post.objects.all()
    # Paginator를 사용하여 모든 포스트를 5개씩 페이지 분할한 후 paginator변수에 할당
    paginator = Paginator(all_posts, 5)

    # GET 파라미터에서 page의 value값을 page_num 변수에 할당
    page_num = request.GET.get('page')
    # paginator의 페이지번호가 page_num인 포스트들을 posts변수에 할당
    if page_num:
        posts = Post.objects.filter(page_num * 9).order_by('-created_date')
    elif not page_num:
        pass

    try:
        posts = paginator.page(page_num)
    # page_num이 숫자형이 아닐 경우에는 1번째 페이지의 posts을 가져옴
    except PageNotAnInteger:
        posts = paginator.page(1)
    # 해당페이지번호가 없을 경우에는 paginator의 마지막 페이지의 posts을 가져옴
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    # 예외처리해준 posts 변수와 comment_form을 렌더링시키기 위해 딕셔너리 삽입
    context = {
        'posts': posts,
        'comment_form': CommentForm(),
    }
    # post_list 템플릿에 만들어준 context dict를 넣어 렌더링함.
    return render(request, 'post/post_list.html', context)


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

    # 2. post_list_original view로 돌아간다.
    # 2-1. redirect를 사용
    #   https://docs.djangoproject.com/en/1.11/topics/http/shortcuts/#redirect
    # return redirect('post:post_list_original')
    # 301 : redirect 코드를 돌려줄 때 가는 페이지
    # redirect는 HttpResponseRedirect와 달리 모델, 뷰페이지를 가지고 페이지를 렌더링
    # 2-2. HttpResponseRedirect
    #   https://docs.djangoproject.com/en/1.11/ref/request-response/#django.http.HttpResponseRedirect
    # 템플릿에서 reverse함수로 url을 조합, 함수를 써주는 것과 위의 redirect()는 결국 같은 기능을 한다.
    # url = reverse('post:post_list_original')
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


# 모든 함수에 로그인 상태 확인 적용해줘야하므로 데코레이터를 사용.
@login_required
def post_create(request):
    # # 로그인이 되어있는 상태인지 확인해야 한다.
    # if not request.user.is_authenticated():
    #     return redirect('member:login')
    if request.method == 'POST':
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # Form 안에서 comment저장을 하기 위해 author를 인수로 할당하고
            # 원래 author를 추가로 저장하기 위해 설정했던 commit=False는 삭제
            post = form.save(author=request.user)
            post.save()

            # PostForm에 comment가 전달되었을 경우 Comment객체 생성
            # comment_string = form.cleaned_data['comment']
            # if comment_string:
            #     post.comment_set.create(
            #         author=request.user,
            #         content=comment_string,
            #     )
            return redirect('post:post_detail', post_pk=post.pk)
        else:
            context = {
                'form': form,
            }
            return render(request, 'post/post_create.html', context)
    form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'post/post_create.html', context)


@post_owner
@login_required
def post_modify(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.method == "POST":
        form = PostForm(data=request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('post:post_detail', post_pk=post.pk)
    else:
        form = PostForm(instance=post)
        context = {
            'form': form,
        }
        return render(request, 'post/post_modify.html', context)


@post_owner
@login_required
def post_delete(request, post_pk):
    # post_pk에 해당하는 Post에 대한 delete요청만을 받음
    # 처리 완료후에는 post_list페이지로 redirect
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == "POST":
        post.delete()
        return redirect('post:post_list_original')
    else:
        # Delete확인창 띄워주기
        context = {
            'post': post,
        }
        return render(request, 'post/post_delete.html', context)


@require_POST
@login_required
def post_like_toggle(request, post_pk):
    # like, unlike 뷰를 따로 만들기 비효율적이므로 toggle로 만들어준다.
    post = get_object_or_404(Post, pk=post_pk)
    # M2M필드가 중간자 모델을 거치지 않을 경우
    # if request.user in post.like_users:
    #    post.like_users.add(request.user)

    # 중간자 모델을 사용할 경우(PostLike)
    # get_or_create를 사용해서 현재 Post와 request.user에 해당하는 PostLike인스턴스 가져옴
    post_like, post_like_created = post.postlike_set.get_or_create(user=request.user)

    # 3. 이후 created여부에 따라 해당 PostLike인스턴스를 삭제 또는 그냥 넘어가기
    # post_like_created가 get_or_create를 통해 새로 PostLike가 만들어졌는지
    # 아니면 기존에 있었는지 여부에 따라 행동 부여
    if not post_like_created:
        # 기존에 PostLike가 있었다면 삭제해준다.
        post_like.delete()

    # 4. 리턴주소는 next가 주어질경우 next로, 없으면 post_detail로
    # next_ = request.GET.get('next')
    # if next_:
    #     return redirect(next_)
    return redirect('post:post_detail', post_pk=post.pk)


def hashtag_post_list(request, tag_name):
    # 1. template 생성
    #   post/hashtag_post_list.html
    #   특정 tag_name이 해당
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(my_comment__tags=tag)
    posts_count = posts.count()

    context = {
        'tag': tag,
        'posts': posts,
        'posts_count': posts_count
    }
    return render(request, 'post/hashtag_post_list.html', context)
