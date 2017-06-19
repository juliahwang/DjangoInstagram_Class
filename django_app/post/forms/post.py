from django import forms
from django.contrib.auth import get_user_model
from member.models import User
from ..models import Post, Comment

User = get_user_model()

class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 장고문서 보기
        self.fields['photo'].required = True
        # comment수정시 my_comment필드와 comment 연결
        if self.instance.my_comment:
            self.fields['comment'].initial = self.instance.my_comment

    comment = forms.CharField(
        # comment는 필수가 아님.
        required=False,
        widget=forms.TextInput
    )

    class Meta:
        model = Post
        fields = (
            'photo',
            'comment',
        )

    # save메서드로 comment필드를 사용해 Comment객체를 생성, DB에 저장
    def save(self, **kwargs):
        # save 할 때 문제가 되는 author를 위해 kwargs로 받은 다음 따로 변수에 지정해준다.
        # commit은 기본으로 True로 주어져있으므로, 주어지지않으면 True로 가져온다.
        commit = kwargs.get('commit', True)
        # author를 딕셔너리에서 빼버린다. 기본값은 None
        author = kwargs.pop('author', None)

        # self.instance.pk가 존재하지 않거나(새로 생성하거나)
        # author가 User인스턴스일 경우
        #
        if not self.instance.pk or isinstance(author, User):
            self.instance.author = author


        # BaseModelForm에서 Meta클래스의 model을 받아 instance를 생성하므로
        # 생성된 instance의 author에 원하는 author를 넣어주면 된다
        #
        # self.instance.author = author
        instance = super().save(**kwargs)

        # commit인수가 True이며 comment필드가 채워져 있을 경우 Comment 생성 로직을 진행
        # 해당 comment는 instance의 my_comment필드를 채워준다.
        #   (이 윗줄에서 super().save()를 실행하기 때문에 현재 위치에서는 author나 pk에 대한 검증이 끝난 상태)

        comment_string = self.cleaned_data['comment']
        # comment가 채워져있을 경우
        if commit and comment_string:
            if instance.my_comment:
                instance.my_comment.content = comment_string
                instance.my_comment.save()
            # my_comment가 없는 경우 Comment객체를 생성해서 my_comment O2O field에 할당
            else:
                instance.my_comment = Comment.objects.create(
                    post=instance,
                    author=instance.author,
                    content=comment_string,
            )
            instance.save()
        # ModelForm의 save()에서 반환해야하는 model의 instance 리턴
        return instance
