from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ..forms import UserEditForm

# Create your views here.
User = get_user_model()

__all__ = (
    'profile',
    'profile_edit',
)


def profile(request, user_pk=None):
    NUM_POSTS_PER_PAGE = 3
    # 1. user_pk에 해당하는 User를 cur_user키로 render
    #   DoesNotExist Exception 발생시 raise Http404
    #  GET 파라미터에 들어온 'page'값 처리
    page = request.GET.get('page')
    try:
        page = int(page) if int(page) > 1 else 1
    except ValueError:
        page = 1
    except Exception as e:
        page = 1
        print(e)
    if user_pk:
        user = User.objects.get(pk=user_pk)
    else:
        user = request.user

    # page * 9만큼 게시물 리턴
    posts = user.post_set.order_by('-created_date')[:page * NUM_POSTS_PER_PAGE]
    post_count = user.post_set.filter(author=user).count()
    # next_page = 현재 page에서 보여주는 Post개수보다 post_count가 클경우 전달받은 page + 1, 아니면 None
    next_page = page + 1 if post_count > page * NUM_POSTS_PER_PAGE else None

    context = {
        'cur_user': user,
        'posts': posts,
        # 페이지변수를 추가하여 템플릿태그에서 if문으로 GET파라미터의 page넘버를 가져오지 않아도 된다
        'page': page,
        'post_count': post_count,
    }
    return render(request, 'member/profile.html', context)
    # 2. member/profile.html 작성, 해당 user정보 보여주기
    #   2-1. 해당 user의 follower, following 목록 보여주기
    # 3. 현재 로그인한 user가 해당 유저(cur_user)를 팔로우하고 있는지 여부 보여주기
    #   3-1. 팔로우중이면 '팔로우 해제'버튼을, 아니라면 '팔로우' 버튼 띄워주기
    # 4 ~ def follow_toggle(request)뷰 생성


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserEditForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            return redirect('member:my_profile')
        # img_profile = request.FILES['img_profile']
        # nickname = request.POST['nickname'] if user.nickname else user.username
        # user.img_profile = img_profile
        # user.nickname = nickname
        # user.save()
    else:
        form = UserEditForm(instance=request.user)
    #     form = UserEditForm(request.GET)
    #     img_profile = request.FILES['cur_profile']
    #     nickname = request.GET['nickname'] if user.nickname else user.username
    context = {
        'form': form,
    }
    return render(request, 'member/profile_edit.html', context)

