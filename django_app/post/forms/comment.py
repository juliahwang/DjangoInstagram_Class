from django import forms
from django.core.exceptions import ValidationError

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

    def clean_content(self):
        """
        content필드에 대한 유효성 검증 메서드
        :return: 3자 이하의 텍스트를 입력하면 에러메세지 표출
        """
        content = self.cleaned_data['content']
        if len(content) < 2:
            raise ValidationError(
                '댓글은 최소 3자이상이어야 합니다'
            )
        return content
