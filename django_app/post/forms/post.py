from django import forms

from ..models import Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 장고문서 보기
        self.fields['photo'].required = True

    comment = forms.CharField(
        # comment는 필수가 아님.
        required= False,
        widget=forms.TextInput
    )

    class Meta:
        model = Post
        fields = (
            'photo',
            'comment',
        )
