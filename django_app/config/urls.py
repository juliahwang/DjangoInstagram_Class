"""instagram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from . import settings, views

app_name = 'config'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    # 로컬호스트 기본 주소를 post/ 페이지로 리다이렉트시키기
    url(r'^$', views.default, name='default'),
    # class뷰를 사용하여 view를 생성하지 않고 바로 리다이렉트 시킬 수 있다.
    # url(r'^$', RedirectView.as_view(pattern_name='post:post_list_original')),

    # post앱의 index뷰를 root url에 연결시킨다.
    # url(r'^$', post_views.index),

    # post앱의 urls.py모듈을 include시킨다.
    url(r'^post/', include('post.urls'), name='post_list_default'),
    url(r'^member/', include('member.urls')),
]
urlpatterns += static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
# static()은 리스트를 만든다. settings의 MEDIA_URL로 왔을 때
# document_root는 settings의 MEDIA_ROOT에서 가져온다.
