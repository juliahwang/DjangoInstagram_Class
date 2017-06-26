from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from ..models import User


__all__ = (
    'follow_toggle_view',
)


@require_POST
@login_required
def follow_toggle_view(request, user_pk):
    next_ = request.GET.get('next')
    following_user = User.objects.get(pk=request.user.pk)
    print(following_user)
    followed_user = get_object_or_404(User, pk=user_pk)
    print(followed_user)
    following_user.follow_toggle(followed_user)
    if next_:
        return redirect(next_)
    return redirect('member:profile', user_pk=followed_user.pk)
