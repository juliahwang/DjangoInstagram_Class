from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    동작
        follow : 내가 다른사람을 follow함
        unfollow : 내가 다른사람에게 한 follow 취소

    속성
        followers : 나를 follow 하고 있는 사람들
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
    nickname = models.CharField(
        max_length=24,
        null=True,
        unique=True
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

    def __str__(self):
        # nickname이 None일 경우에는 username 반환
        return self.nickname or self.username

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

    def is_follow(self, user):
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
    def followers(self):
        # 나를 follow중인 User QuerySet
        relation = self.follow_relation.all()
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