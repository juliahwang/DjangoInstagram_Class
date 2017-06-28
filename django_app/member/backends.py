from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
# ModelBackend를 커스터마이징.
# authenticate()와 get_user()는 반드시 정의해줘야함.
from config import settings

User = get_user_model()


class FacebookBackend:
    # 인증 메서드 - 페이스북으로 로그인한 user를 .get으로 찾아서 있으면 반환, 없으면 None 반환
    def authenticate(self, request, facebook_id):
        username = '{}_{}_{}'.format(
            User.USER_TYPE_FACEBOOK,
            settings.FACEBOOK_APP_ID,
            facebook_id,
        )
        try:
            user = User.objects.get(
                user_type=User.USER_TYPE_FACEBOOK,
                username=username
            )
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(user_id)
        except User.DoesNotExist:
            return None