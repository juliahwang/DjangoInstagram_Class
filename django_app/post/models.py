from django.db import models
"""
member application 생성
    User모델 구현
        username, nickname
이후 해당 User모델을 Post나 Comment에서 author나 
user항목으로 참조
"""
# Create your models here.
class Post(models.Model):
    pass


class Comment(models.Model):
    pass


class PostLike(models.Model):
    pass

