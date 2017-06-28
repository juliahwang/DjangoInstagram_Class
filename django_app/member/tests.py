from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, TransactionTestCase

from config import settings

User = get_user_model()


# Create your tests here.
class UserModelTest(TransactionTestCase):
    DUMMY_USERNAME = 'username'
    DUMMY_PASSWORD = 'password'

    # 내부 기능을 사용하지 않으므로 스테틱 메서드로 정의해준다
    @staticmethod
    def make_users(num):
        return [User.objects.create_user(username='username {}'.format(i)) for i in range(num)]

    def test_fields_default_value(self):
        """
        더미 유저를 생성해 필드의 기본값이 원하는 형태로 들어가있는지 확인
        :return: 각 필드별 기본값 일치 현황
        """
        user = User.objects.create_user(
            username=self.DUMMY_USERNAME,
            password=self.DUMMY_PASSWORD,
        )
        self.assertEqual(user.first_name, '')  # first_name 필드
        self.assertEqual(user.last_name, '')  # last_name 필드
        self.assertEqual(user.email, '')  # email 필드
        self.assertEqual(user.user_type, User.USER_TYPE_DJANGO)  # user_type 필드
        self.assertEqual(user.nickname, None)  # nickname 필드
        self.assertEqual(user.img_profile, '')  # img_profile 필드
        self.assertEqual(user.relations.count(), 0)  # relations 필드

    def test_follow(self):
        """
        임의의 유저 4명을 생성하여 팔로우 메서드로 팔로우 기능을 테스트한다.
        :return: 임의 유저 4명을 생성해 팔로우 관계 형성
        """
        def follow_test_helper(source, following, non_following=None):
            for target in following:
                self.assertIn(target, source.following)
                self.assertIn(source, target.follower)
                self.assertTrue(source.is_following(target))
                self.assertTrue(target.is_follower(source))

                # user1에 대한 관계가 생성되었는지 테스트를 직접 메서드로 만들었다(위)
                # self.assertIn(user2, user1.following)
                # self.assertIn(user3, user1.following)
                # self.assertIn(user4, user1.following)
                # self.assertIn(user1, user2.follower)
                # self.assertIn(user1, user3.follower)
                # self.assertIn(user1, user4.follower)
                # self.assertTrue(user1.is_following(user2))
                # self.assertTrue(user1.is_following(user3))
                # self.assertTrue(user1.is_following(user4))
                # self.assertTrue(user2.is_follower(user1))
                # self.assertTrue(user3.is_follower(user1))
                # self.assertTrue(user4.is_follower(user1))
            # following 되지 않은 관계도 확실히 테스트해준다.
            for target in non_following:
                self.assertNotIn(target, source.following)
                self.assertNotIn(source, target.follower)
                self.assertFalse(source.is_following(target))
                self.assertFalse(target.is_follower(source))

        user1, user2, user3, user4 = self.make_users(4)
        user1.follow(user2)
        user1.follow(user3)
        user1.follow(user4)

        user2.follow(user3)
        user2.follow(user4)

        user3.follow(user4)

        # user1에 대한 테스트
        follow_test_helper(
            source=user1,
            following=[user2, user3, user4],
            non_following=[],
        )
        follow_test_helper(
            source=user2,
            following=[user3, user4],
            non_following=[user1],
        )
        follow_test_helper(
            source=user3,
            following=[user4],
            non_following=[user1, user2],
        )
        follow_test_helper(
            source=user4,
            following=[],
            non_following=[user1, user2, user3],
        )

    def test_unfollow(self):
        """unfollow 테스트 메서드"""
        user1, user2 = self.make_users(2)
        user1.follow(user2)

        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user2.is_follower(user1))
        self.assertIn(user1, user2.follower)
        self.assertIn(user2, user1.following)

        user1.unfollow(user2)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user2.is_follower(user1))
        self.assertNotIn(user1, user2.follower)
        self.assertNotIn(user2, user1.following)

    def test_follow_toggle(self):
        """follow_toggle 메서드 테스트"""
        user1, user2 = self.make_users(2)
        user1.follow_toggle(user2)

        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user2.is_follower(user1))
        self.assertIn(user1, user2.follower)
        self.assertIn(user2, user1.following)

        user1.follow_toggle(user2)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user2.is_follower(user1))
        self.assertNotIn(user1, user2.follower)
        self.assertNotIn(user2, user1.following)


class UserModelManagerTest(TransactionTestCase):
    def test_get_or_create_facebook_user(self):
        test_last_name = 'test_last_name'
        test_first_name = 'test_first_name'
        test_email = 'test_email@email.com'
        user_info = {
            'id': 'dummy_facebook_id',
            'last_name': test_last_name,
            'first_name': test_first_name,
            'email': test_email,
        }
        # 만든 더미 user_info로 테스트 페이스북 유저를 DB에 생성한다.
        user = User.objects.get_or_create_facebook_user(user_info)

        # 아이디값이 유효한지(같은지) 테스트
        self.assertEqual(
            user.username,
            '{}_{}_{}'.format(
                User.USER_TYPE_FACEBOOK,
                settings.FACEBOOK_APP_ID,
                user_info['id'],
            )
        )
        # user_type이 'f'로 지정되어있는지 테스트
        self.assertEqual(user.user_type, User.USER_TYPE_FACEBOOK)
        # 그 외 속성 테스트
        self.assertEqual(user.first_name, test_first_name)
        self.assertEqual(user.last_name, test_last_name)
        self.assertEqual(user.email, test_email)



