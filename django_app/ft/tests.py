# 사용자 기능 테스트
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver

from member.models import User


class FirstPageTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.quit()

    def test_root_url_redirect_to_post_list(self):
        # 현재 브라우저의 live_server_url을 가져와 현재 페이지를 프린트해본다
        self.browser.get(self.live_server_url)
        print(self.live_server_url)
        # http://localhost:64550
        print(self.browser.current_url)
        # http://localhost:63846/post/ ... 잘 간다!

        self.assertEqual(
            self.live_server_url + '/post/',
            self.browser.current_url,
        )

        # 위와 같은 것을 테스트하지만 post_list 뷰의 url을 reverse해서 일치하는지 볼 수도 있다.
        post_list_url = reverse('post:post_list')
        self.assertEqual(
            self.live_server_url + post_list_url,
            self.browser.current_url
        )

    # 로그인하지 않으면 login페이지로 리다이렉트시키는 뷰 검사
    def test_not_authenticated_user_redirect_to_login_view(self):
        urls = [
            # 로그인하지 않았을 때 프로필 아이콘을 클릭하는 경우 리다이렉트 해줘야함.
            # -> profile 뷰에 조건문을 넣어준다.
            '/member/profile/',
            '/member/profile/edit/',
            '/post/create/',
            # post_pk가 있는 url은 찾지 못하므로 따로 테스트해준다.
            # 'post/modify/',
            # 'post/delete/',
        ]
        for url in urls:
            self.browser.get(self.live_server_url + url)
            # assertEqual 말고 In을 쓴다. 왜냐하면 for문을 돌면서 이전 페이지에 대한
            # next 파라미터가 붙으므로 비교하는 url이 같을 수 없기 때문이다.
            self.assertIn(
                self.live_server_url + '/member/login/',
                self.browser.current_url,
            )

    def test_not_authenticated_user_can_view_login_form(self):
        test_username = 'username'
        test_password = 'password'
        User.objects.create_user(
            username=test_username,
            password=test_password,
        )
        # 로그인하지 않은 유저가 화면의 로그인 폼을 통해서 로그인할 수 있는지 테스트
        self.browser.get(self.live_server_url)
        form_login = self.browser.find_element_by_class_name('form-inline-login')
        # form에서 자동으로 'id_<필드명>'을 생성해준다.
        input_username = self.browser.find_element_by_id('id_username')
        input_password = self.browser.find_element_by_id('id_password')
        button_submit = form_login.find_element_by_tag_name('button')

        # 폼에 값을 입력하고 로그인버튼 클릭
        input_username.send_keys(test_username)
        input_password.send_keys(test_password)
        # 해당 버튼을 클릭하게 하는 click() 메서드 실행
        button_submit.click()

        print(self.browser.current_url)

        # 화면에 로그인한 유저의 유저명이 표시되는지 확인
        top_header = self.browser.find_element_by_class_name('top-header')
        self.assertIn(
            test_username,
            top_header.text
        )
