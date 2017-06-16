from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
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

    def __str__(self):
        return self.nickname
