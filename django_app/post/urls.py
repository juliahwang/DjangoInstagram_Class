from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),

    # post_detail과 매칭 ex_ /post/3/$, /post/345/$
    # 숫자 1개 이상을 변수로 전달하기 위해 그룹화하고, 그룹명을 post_pk로 지정해준다.
    # 정규표현식에서 매칭된 그룹을 키워드인수로 반환하는 방법 : 그룹 앞부분에 ?P<이름> 지정
    # 일치하는 패턴을 가진 url을 찾을 경우 views로 가서 post_detail을 실행한다.
    url(r'^(?P<post_pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^create/$', views.post_create, name='post_create'),
    url(r'^(?P<post_pk>\d+)/modify/$', views.post_modify, name='post_modify')
]