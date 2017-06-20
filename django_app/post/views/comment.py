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
    post = get_object_or_404(Post, pk=post_pk)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('post:post_detail', post_pk=post.pk)
    # GET 요청일 때 보여줄 페이지는 필요없음


def comment_modify(request, post_pk):
    # 코멘트 수정
    pass


def comment_delete(request, post_pk, comment_pk):
    pass


def post_anyway(request):
    return redirect('post:post_anyway')
