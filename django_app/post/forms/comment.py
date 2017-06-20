from django import forms

from member.models import User
from ..models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        # fields를 튜플로 하지 않은 이유는 나중에 수정이 가능하므로.
        fields = [
            'content',
        ]
        # 기존 필드를 수정하여 쓸 때는 widget 속성을 부여한다.
        widgets = {
            'content': forms.TextInput(
                attrs={
                    'class': 'input-comment',
                    'placeholder': '댓글을 입력하세요',
                }
            )
        }

    content = forms.CharField(
        required=True,
        widget=forms.TextInput
    )

    def save(self, **kwargs):
        commit = kwargs.get('commit', True)
        author = kwargs.pop('author', None)

        if not self.instance.pk or isinstance(author, User):
            self.instance.author = author

        instance = super().save(**kwargs)

        comment_string = self.cleaned_data['content']
        if commit and comment_string:
            if instance.content:
                instance.content = comment_string
                instance.save()
            else:
                instance.content = Comment.objects.create(
                    author=instance.author,
                    content=comment_string,
                )
            instance.save()
        return instance
