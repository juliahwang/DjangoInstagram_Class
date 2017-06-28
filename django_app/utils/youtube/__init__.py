import requests
from googleapiclient.discovery import build

from config import settings

__all__ = (
    'search',
)


def search(request, q):
    youtube_search_api = 'https://www.googleapis.com/youtube/v3/search'
    redirect_search_list_api_params = {
        'part': 'snippet',
        'key': settings.YOUTUBE_KEY,
        'maxResults': 10,
        'type': 'video',
        # requests.get을 사용한 결과를 변수에 할당하고
        'q': q,
    }
    response = requests.get(youtube_search_api, params=redirect_search_list_api_params)
    data = response.json()
    return data


def search_with_temp(q):
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSIONS = 'v3'
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSIONS,
        developerKey=settings.YOUTUBE_KEY,
    )

    search_response = youtube.search().list(
        q=q,
        part='id,snippet',
        maxResults=10,
        type='video'
    ).execute()
    return search_response

