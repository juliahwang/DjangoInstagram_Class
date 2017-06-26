# 기존 내장 이미지필드 클래스 자체에 사용자 편의용 메서드를 정의
# 이미지필드를 출력해보면 FieldFile형 자료가 출력된다.
# <FieldFile abc.jpg>
from django.db.models.fields.files import ImageFieldFile, ImageField


class CustomImageFieldFile(ImageFieldFile):
    # 기존 FieldFile 클래스의 url메서드 오버라이드
    @property
    def url(self):
        try:
            return super().url
        except ValueError:
            # 예외가 일어날 때만 import하여 static폴더를 찾아 이미지를 돌려준다.
            from django.contrib.staticfiles.storage import staticfiles_storage
            return staticfiles_storage.url(self.field.static_image_path)


class CustomImageField(ImageField):
    attr_class = CustomImageFieldFile

    # 사용자정의한 CustomImageField의 인자를 새로 지정해주기 위해
    # 초기화 메서드 오버라이드
    def __init__(self, *args, **kwargs):
        # img_profile의 인자 default_static_image를 꺼내와
        # 원하는 이미지로 바꿔준 후 이를 static_image_path 변수에 할당
        self.static_image_path = kwargs.pop('default_static_image', 'images/no_image.png')
        # 나머지 부모 초기화 메서드는 그대로 호출해 사용.
        super().__init__(*args, **kwargs)

