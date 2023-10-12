from typing import Iterable, Optional
from django.db import models
from django.contrib.auth import get_user_model 
from django.utils.text import slugify

User = get_user_model()

class Group(models.Model):
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug=slugify(self.title)
        super(Group, self).save(*args, **kwargs)

    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField()


class Post(models.Model): 
    def __str__(self) -> str:
        return self.text
    text = models.TextField() 
    pub_date = models.DateTimeField("date published", auto_now_add=True) 
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, related_name="posts")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    class Meta:
        ordering=['-pub_date']
    

class Comment(models.Model):
    def __str__(self) -> str:
        return self.text
    post=models.ForeignKey(Post,on_delete=models.CASCADE, related_name='comments', verbose_name="Комментарий к записи",help_text="Добавьте комментарий к записи")
    author=models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="Автор комментария")
    text=models.TextField(blank=False, max_length=350, verbose_name='Текст комментария')
    created=models.DateTimeField('date created', auto_now_add=True)
    class Meta:
        ordering=['-created']

class Follow(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author=models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    