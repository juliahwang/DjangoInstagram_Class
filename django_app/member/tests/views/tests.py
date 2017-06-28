from django.test import TestCase
from django.urls import reverse, resolve
from member import views


class LoginViewTest(TestCase):
    VIEW_URL = 'member/login/'
    VIEW_URL_NAME = 'member:login'

    def test_url_equal_reverse_url_name(self):
        # 주어진 VIEW_URL과 VIEW_URL_NAME을 reverse()한 결과가 같은지 테스트
        self.assertEqual(self.VIEW_URL, reverse(self.VIEW_URL_NAME))

    def test_uses_resolves_to_login_view(self):
        # login view가 특정 url을 사용하고 있는지 테스트
        # 해당 url이 function(view)을 참조하는지 보는 resolve()메서드 사용
        found = resolve(self.VIEW_URL)
        # 특정 view에 해당하는 함수 (.func속성)과 views.login함수가 같은 것인지 테스트
        self.assertEqual(found.func, views.login)

    def test_uses_login_template(self):
        # login의 url과 실제 client의 url이 일치하는지 테스트하면 같은 템플릿을 쓰는 지 알 수 있다
        url = reverse('member:login')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'member/login.html')

