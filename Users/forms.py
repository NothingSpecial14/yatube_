from django.contrib.auth. forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError
from posts.models import Post, Comment, Follow
from django.utils.translation import gettext_lazy as _
User=get_user_model()

class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model=User
        fields=["first_name", "last_name", "username", "email"]

def validate_text(value):
    if not value:
        raise ValidationError('Вы не ввели текст', params={'value':value})

class PostForm(ModelForm):
    class Meta():
        model=Post
        fields=['group', 'text', 'image']
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['group'].required=False
            self.fields['text'].validators=[validate_text]
        
class CommentForm(ModelForm):
    class Meta():
        model=Comment
        fields=['text']
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['text'].validators=[validate_text]     