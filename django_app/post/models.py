import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

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
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    photo = models.ImageField(upload_to='post', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    # related_name='+'로 지정할 경우 역참조를 생성하지 않는다
    my_comment = models.OneToOneField('comment', related_name='+', blank=True, null=True)
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


class Comment(models.Model):
    post = models.ForeignKey(Post)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CommentLike',
        related_name='like_comments',
    )

    def save(self, *args, **kwargs):
        # 새로생성할 경우에는 일단 데이터를 저장한다.
        if not self.pk:
            super().save(*args, **kwargs)
        # 아니면 해시태그 생성 메서드를 실행하고 저장한다.
        # save 메서드가 너무 커지므로 따로 메서드를 정의해주고(html생성) 실행한다.
        self.make_html_content_and_add_tags()
        super().save(*args, **kwargs)

    def make_html_content_and_add_tags(self):
        # 해시태그에 해당하는 정규표현식
        p = re.compile(r'(#\w+)')
        # findall 메서드로 해시태그의 문자열을 가져옴
        tag_name_list = re.findall(p, self.content)
        # 기존 content(Comment내용)을 변수에 할당
        ori_content = self.content
        # 문자열을 순회하며
        for tag_name in tag_name_list:
            # Tag객체를 가져오거나 없으면 생성하여 tag(#)를 생략해준다.
            tag, _ = Tag.objects.get_or_create(name=tag_name.replace('#', ''))
            # 기존 content의 내용 변경
            change_tag = '<a href="{url}" class="hash-tag">{tag_name}</a>'.format(
                url=reverse('post:hashtag_post_list', kwargs={'tag_name': tag_name.replace('#', '')}),
                tag_name=tag_name,
            )
            ori_content = re.sub(r'{}(?![<\w])'.format(tag_name), change_tag, ori_content, count=1)
            # content에 포함된 Tag목록을 자신의 tags필드에 추가
            if not self.tags.filter(pk=tag.pk).exists():
                self.tags.add(tag)
        # 편집이 완료된 문자열을 html_content에 저장
        self.html_content = ori_content
        super().save(update_fields=['html_content'])


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_date = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return 'Tag({})'.format(self.name)
