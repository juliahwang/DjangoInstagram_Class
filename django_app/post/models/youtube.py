from django.db import models

__all__ = [
    'Video',
]

# 뷰에서 많은 일을 하는 것은 MTV모델에 반하므로 매니저를 생성해서 오브젝트로 만들어준다.
# 매니저 안에 생성하는 루틴을 넣어놓고 Video모델에서 objects로 호출하면 실행된다.
class VideoManager(models.Manager):
    def create_from_search_result(self, result):
        youtube_id = result['id']['videoId']
        title = result['snippet']['title']
        description = result['snippet']['description']
        url_thumbnail = result['snippet']['thumbnails']['high']['url']
        video, video_created = self.get_or_create(
            youtube_id=youtube_id,
            defaults={
                'title': title,
                'description': description,
                'url_thumbnail': url_thumbnail,
            }
        )
        print('Video({}) is {}'.format(
            video.title,
            'created' if video_created else "Already exist"
        ))
        return video


class Video(models.Model):
    youtube_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url_thumbnail = models.CharField(max_length=200)

    objects = VideoManager()

    def __str__(self):
        return self.title
