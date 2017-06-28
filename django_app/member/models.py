import re

import requests
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from config import settings
from utils.fields import CustomImageField
from django.db import models


class UserManager(DefaultUserManager):
    def get_or_create_facebook_user(self, user_info):
        # 고유 username패턴을 만들어준다.
        username = '{}_{}_{}'.format(
            User.USER_TYPE_FACEBOOK,
            settings.FACEBOOK_APP_ID,
            user_info['id']
        )
        user, user_created = self.get_or_create(
            username=username,
            user_type=self.model.USER_TYPE_FACEBOOK,
            defaults={
                'last_name': user_info.get('last_name'),
                'first_name': user_info.get('first_name'),
                'email': user_info.get('email', ''),
            }
        )
        # 유저가 새로 생성되었을 때만 이미지 파일을 불러옴.
        # user_info에 'picture'의 value값이 있어야 다음 if의 실행문을 실행한다.
        if user_created and user_info.get('picture'):
            ### 메모리상에 (url로) 존재하던 이미지파일을 실제 파일로 서버에 저장하는 법
            # 프로필 이미지 url 가져오기
            url_picture = user_info['picture']['data']['url']

            # 이미지파일 확장자 가져오는 정규표현식
            p = re.compile(r'.*\.([^?]+)')
            file_ext = re.search(p, url_picture).group(1)
            file_name = '{}.{}'.format(
                user.pk,
                file_ext
            )
            # 이미지 파일을 임시저장할 파일객체
            # delete=False 옵션을 주면 객체가 사라져도(id를 지워도) 파일이 지워지지 않는다.
            temp_file = NamedTemporaryFile()

            # 프로필 이미지 URL에 대한 get요청 (이미지 다운로드)
            response = requests.get(url_picture)

            # 요청결과를 temp_file에 기록
            temp_file.write(response.content)

            # ImageField의 save()메서드를 호출해서 해당 임시파일 객체를 주어진 이름의 파일로 저장
            user.img_profile.save('profile.jpg', temp_file)
        return user


class User(AbstractUser):
    """
    동작
        follow : 내가 다른사람을 follow함
        unfollow : 내가 다른사람에게 한 follow 취소

    속성
        follower : 나를 follow 하고 있는 사람들
        follower : 나를 follow한 사람
        following : 내가 follow하고 있는 사람
        friend : 맞팔
        friends : 복수 맞팔
        없음 : 내가 follow하고 있는 사람 1 명
    """
    # 이 User모델을 AUTH_USER_MODEL로 사용하도록 settings.py에 설정
    # 유일한 nickname을 가지려면 blank=True가 아니라 null=True사용
    # blank=True를 넣게 되면 2명 이상의 사용자가 닉네임을 입력하지 않을 때
    # "" 값을 비교해버리므로 입력하지 않으면 계속 에러가 난다
    # null=True로 하면 아예 없는 값이므로 비교자체가 불가능하다.
    USER_TYPE_DJANGO = 'd'
    USER_TYPE_FACEBOOK = 'f'
    USER_TYPE_CHOICES = (
        (USER_TYPE_DJANGO, 'Django'),
        (USER_TYPE_FACEBOOK, 'Facebook'),
    )
    # 유저타입 기본은 Django, 페이스북 로그인시 USER_TYPE_FACEBOOK값을 갖도록 함.
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, default=USER_TYPE_DJANGO)
    nickname = models.CharField(
        max_length=24,
        null=True,
        unique=True
    )
    img_profile = CustomImageField(
        upload_to='user',
        blank=True,
        # 기본 설정 이미지를 세팅했지만 원하는 이미지를 추가로 넣어줄 수도 있다
        # default_static_image='images/profile.png'
    )
    ### self 상속
    # M2M필드는 비대칭적이지만 self 상속하게 되면 대칭이 된다(following)
    # 그리고 대칭관계라면 through로 참조, 역참조 관계를 알려주는 것이 아니라 방향성을 지정해줘야한다.
    # symmetrical= False를 정해주면 역참조명이 생기는 것이 아니라 중간자모델의 필드간 관계가 동등해지고
    # from_user와 to_user의 참조값이 대등하도록 related_name을 사용해줘야한다.
    relations = models.ManyToManyField(
        'self',
        through='Relation',
        symmetrical=False,
    )

    objects = UserManager()

    def __str__(self):
        # nickname이 None일 경우에는 username 반환
        return self.nickname or self.username

    # def post_count(self):
    #     return self.post_set.filter(author=self).count()

    def follow(self, user):
        # user가 User의 객체(형, 타입, =클래스)인지 검사
        # is_authenticated는 인증여부이므로 상관없다. user객체인지 아닌지만 검사하면 됨.
        if not isinstance(user, User):
            raise ValueError
        # 해당 user를 follow하는 Relation생성
        # 이미 follow 상태일 경우 아무일도 하지 않음.
        Relation.objects.get_or_create(from_user=self, to_user=user)

        # self로 주어진 User로부터 Relation의 from_user에 해당하는 RelatedManager를 사용
        # following시 가장 적합한 방법
        self.follow_relation.get_or_create(to_user=user)

        # user로 주어진 User로부터 Relation의 to_user에 해당하는 RelatedManager를 사용
        user.follower_relation.get_or_create(from_user=self)

    def unfollow(self, user):
        # follow 메서드의 반대역할
        Relation.objects.filter(
            from_user=self,
            to_user=user,
        ).delete()

    def is_following(self, user):
        # 해당 user를 내가 follow하고 있는지 bool 여부 반환
        return Relation.objects.filter(from_user=self, to_user=user).exists()
        # if status:
        #     return '{}가 {}를 팔로우하고 있습니다.'.format(self, user)
        # else:
        #     return '{}가 {}를 팔로우하지 않았습니다.'.format(self, user)

    def is_follower(self, user):
        # 해당 user가 나를 follow하고 있는지 bool 여부 반환
        return self.follower_relation.filter(from_user=user).exists()

    def follow_toggle(self, user):
        # 이미 follow상태면 unfollow로, 아니면 follow상태로 만듦
        if not isinstance(user, User):
            raise ValueError
        following, follow_created = self.follow_relation.get_or_create(to_user=user)
        if not follow_created:
            # Relation.objects.filter(from_user=self, to_user=user).delete()
            following.delete()
        return following

    @property
    def following(self):
        # 내가 follow중인 User QuerySet
        relation = self.follow_relation.all()
        # 아래 코드는 위와 같다. 하지만 위쪽이 더 의미가 맞음.
        # relation = Relation.objects.filter(from_user=self)
        return User.objects.filter(pk__in=relation.values('to_user'))

    @property
    def follower(self):
        # 나를 follow중인 User QuerySet
        relation = self.follower_relation.all()
        return User.objects.filter(pk__in=relation.values('from_user'))


class Relation(models.Model):
    # 내가 팔로우하는 사람들의 관계를 related_name으로 가져온다.
    from_user = models.ForeignKey(User, related_name='follow_relation')
    # 나를 팔로우하고 있는 사람들의 관계를 related_name으로 가져온다.
    to_user = models.ForeignKey(User, related_name='follower_relation')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}이/가 {}를 팔로우한다.'.format(
            self.from_user,
            self.to_user
        )

    # 한번 관계가 생긴 로우가 중복으로 만들어지지 않도록 제한
    class Meta:
        unique_together = (
            ('from_user', 'to_user'),
        )