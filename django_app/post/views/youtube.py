import requests
from django import utils
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from config import settings
from post.models import Video, Post, Comment
from utils import youtube

__all__ = (
    'youtube_search',
    'post_create_with_video',
)


@login_required
def youtube_search_original(request):
    # search list API를 이용해서 (type: video, maxResults: 10)
    youtube_search_list_api = 'https://www.googleapis.com/youtube/v3/search'
    q = request.GET.get('q')
    # request.GET.get('q')에 데이터가 있을 경우
    if q:
        redirect_search_list_api_params = {
            'part': 'snippet',
            'key': settings.YOUTUBE_KEY,
            'maxResults': 10,
            'type': 'video',
            # requests.get을 사용한 결과를 변수에 할당하고
            'q': q,
        }
        # 해당 변수를 템플릿에 표시
        response = requests.get(youtube_search_list_api, params=redirect_search_list_api_params)
        data = response.json()
        for item in data['items']:
            Video.objects.create_from_search_result(item)

        # videos = Video.objects.filter(title__contains=q)
        # videos = Video.objects.filter(Q(title__contains=q) | Q(description__contains=q))

        # 검색어가 빈칸단위로 구분되어 있을 때 빈칸으로 split한 값들을 각각 포함하고 있는지 and연산
        # 원초적인 방법 - filter링 반복하기
        # videos = Video.objects.all()
        # for cur_q in q.split(' '):
        #     videos.filter(title__contains=cur_q)

        # regex사용법
        # and 연산 - 검색어 둘다 포함하는 것이 나온다.
        # re_pattern = ''.join(['(?=.*{})'.format(item) for item in q.split()])

        # or 연산 - 검색어 하나만 포함하는 자료도 나온다.
        re_pattern = '|'.join(['({})'.format(item) for item in q.split()])
        videos = Video.objects.filter(title__iregex=r'{}'.format(re_pattern))
        # videos = Video.objects.filter(Q(title__iregex=r'{}'.format(re_pattern)) |
        #                               Q(description__iregex=r'{}'.format(re_pattern)
        # ))
        context = {
            'videos': videos,
            're_pattern': re_pattern,
        }
    # q값이 없을 때
    else:
        context = {}
    return render(request, 'post/youtube_search.html', context)


def youtube_search(request):
    q = request.GET.get('q')
    context = dict()
    if q:
        data = youtube.search(request, q)
        for item in data['items']:
            Video.objects.create_from_search_result(item)
        re_pattern = '|'.join(['({})'.format(item) for item in q.split()])
        videos = Video.objects.filter(title__regex=r'{}'.format(re_pattern))
        context = {
            'videos': videos,
            're_pattern': re_pattern,
        }
    # q값이 없을 때
    else:
        context = {}
    return render(request, 'post/youtube_search.html', context)


@require_POST
@login_required
def post_create_with_video(request):
    video_pk = request.POST['video_pk']
    video = get_object_or_404(Video, pk=video_pk)

    post = Post.objects.create(
        author=request.user,
        video=video,
    )
    post.my_comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=video.title,
    )
    return redirect('post:post_detail', post_pk=post.pk)
