from django.conf.urls import url

from . import views

app_name = 'member'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    # 자기자신의 url을 profile/로 접근하기 위해 따로 지정.
    url(r'^profile/$', views.profile, name='my_profile'),
    url(r'^profile/(?P<user_pk>\d+)/$', views.profile, name='profile'),
    # follow
    url(r'^follow_toggle/(?P<user_pk>\d+)/$', views.follow_toggle_view, name='follow_toggle_view'),
]