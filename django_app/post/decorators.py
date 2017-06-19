# 글을 수정할 때 글을 만든 유저만 수정할 수 있도록 하는 커스텀 데코레이터를 만든다.
from django.core.exceptions import PermissionDenied

from .models import Post


def post_owner(f):
    def wrap(request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['post_pk'])
        if request.user == post.author:
            return f(request, *args, **kwargs)
        raise PermissionDenied
    return wrap