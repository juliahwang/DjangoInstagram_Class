from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from post.forms import CommentForm
from post.models import Post

__all__ = (
    'comment_create',
    'comment_delete',
    'comment_modify',
    'post_anyway',
)

# POST요청만 보내는 함수임을 데코레이터로 알려준다.(조건문사용안해도 됨)
@require_POST
@login_required
def comment_create(request, post_pk):
    # POST 요청을 받아 Comment객체를 생성 후 post_detail페이지로 redirect
    # CommentForm을 만들어서 해당 ModelForm안에서 생성/수정가능하도록 사용
    # URL에 전달된 post_pk로 특정 Post 객체 가져옴
    post = get_object_or_404(Post, pk=post_pk)
    # GET요청시 parameter중 'next'의 value값을 next_에 할당
    next_ = request.GET.get('next')
    # CommentForm data binding
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # comment변수에 commit=False의 결과인 인스턴스를 할당
        comment = form.save(commit=False)
        # comment의 author와 post를 각각 지정해준다.
        comment.author = request.user
        comment.post = post
        # save() 메서드 실행
        comment.save()
        # next로 이동할 url이 있다면 그쪽으로 이동시킴
    else:
        result = '<br>'.join(['<br>'.join(v) for v in form.errors.values()])
        messages.error(request, result)
    if next_:
        return redirect(next_)
    # next_값이 없다면 post_detail로 이동
    return redirect('post:post_detail', post_pk=post.pk)
    # GET 요청일 때 보여줄 페이지는 필요없음


def comment_modify(request, post_pk):
    # 코멘트 수정
    if request.method == "POST":
        form = CommentForm(data=request.POST)
        form.save()
    else:
        form = CommentForm()


def comment_delete(request, post_pk, comment_pk):
    pass


def post_anyway(request):
    return redirect('post:post_anyway')
