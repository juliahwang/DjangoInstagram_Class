from django.db import models
from django.contrib.auth.models import User

"""
member application 생성
    User모델 구현
        username, nickname
이후 해당 User모델을 Post나 Comment에서 author나 
user항목으로 참조
"""


# Create your models here.


class Post(models.Model):
    # Django가 제공하는 기본 User로 연결되도록 수정
    author = models.ForeignKey(User)
    photo = models.ImageField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    like_users = models.ManyToManyField(
        User,
        related_name='like_posts',
        # User에서 받아온 컬럼이 2개 있으므로 이름을 바꿔준다.
    )
    tags = models.ManyToManyField('Tag')


class Comment(models.Model):
    post = models.ForeignKey(Post)
    author = models.ForeignKey(User)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return 'Tag({})'.format(self.name)
