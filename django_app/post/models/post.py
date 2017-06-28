from django.conf import settings
from django.db import models

from utils.fields import CustomImageField

"""
member application 생성
    User모델 구현
        username, nickname
이후 해당 User모델을 Post나 Comment에서 author나
user항목으로 참조
"""

# Create your models here.
__all__ = [
    'Post',
    'PostLike',
]


class Post(models.Model):
    # Django가 제공하는 기본 User로 연결되도록 수정
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    photo = CustomImageField(upload_to='post', blank=True)
    # 나중에 만들어지는 클래스의 경우에는 ''를 붙이고 import를 하지 않는다.
    video = models.ForeignKey(
        'Video',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    # related_name='+'로 지정할 경우 역참조를 생성하지 않는다
    my_comment = models.OneToOneField('Comment', related_name='+', blank=True, null=True)
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PostLike',
        related_name='like_posts',
        # User에서 받아온 컬럼이 2개 있으므로 이름을 바꿔준다.
    )

    # 내림차순 정렬
    class Meta:
        ordering = ['-pk', ]

    def add_comment(self, user, content):
        return self.comment_set.create(
            author=user,
            content=content,
        )

    # def add_tag(self, tag_name):
    #     # tags에 tag매개변수로 전달된 값str을
    #     # name으로 갖는 Tag 객체를 (이미 존재하면) 가져오고 없으면 생성하여 자신의 tags에 추가
    #     # 이 경우에는 get_or_create()를 사용!
    #     tag, tag_created = Tag.objects.get_or_create(name=tag_name)
    #     if not self.tags.filter(name=tag_name).exists():
    #         self.tags.add(tag)

    def like_count(self):
        # 자신을 like하고 있는 user수 리턴
        return self.like_users.count()

    def liked_username(self):
        # 해당 post를 좋아하는 user들의 이름 나열
        return '{}'.format(', '.join([i.username for i in self.like_users.all()]))


class PostLike(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_date = models.DateTimeField(auto_now_add=True)
