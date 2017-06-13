from http.client import HTTPResponse

from django.shortcuts import render, get_object_or_404, redirect
from config.settings import MEDIA_ROOT
# Create your views here.
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
    # post_pk에 해당하는 Post 객체를 리턴 / 보여줌
    post = get_object_or_404(Post, pk=post_pk)
    context = {
        'post': post,
    }
    return render(request, 'post/post_detail.html', context=context)


def post_create(request):
    # POST요청을 받아 Post객체를 생성 후 post_list페이지로 redirect
    context = {
    }
    if request.method == 'GET':
        return render(request, 'post/post_create.html', context=context)
    else:
        data = request.POST
        print(data)
        photo = request.FILES['photoupload']
        author = User.objects.first()
        Post.objects.create(author=author, photo=photo)
        return redirect('post_list')


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
