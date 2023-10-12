from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow
from Users.forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

User=get_user_model()

#@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group=get_object_or_404(Group, slug=slug)
    post_list=Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator=Paginator(post_list, 10)
    page_number=request.GET.get('page')
    page=paginator.get_page(page_number)
    return render(request, "group.html", {"page":page, "group":group, "paginator":paginator})

def profile(request, username):
    user=get_object_or_404(User, username__iexact=username)
    username=user.username
    user_first_name=user.first_name
    user_last_name=user.last_name
    try:
        user_obj=User.objects.get(username=request.user.username)
        following=user.following.filter(user=user_obj).exists()
    except User.DoesNotExist:
        following=False
    post_count=Post.objects.filter(author=user).count()
    followers_count=Follow.objects.filter(author=user).count()
    followings_count=Follow.objects.filter(user=user).count()
    post_list=Post.objects.filter(author=user).all()
    paginator=Paginator(post_list, 10)
    page_number=request.GET.get('page')
    page=paginator.get_page(page_number)
    return render(request, 'profile.html', {"username":username, 
                                            "user_first_name":user_first_name, 
                                            "user_last_name":user_last_name, 
                                            "post_count":post_count,
                                            "followers_count":followers_count,
                                            "followings_count":followings_count, 
                                            "post_list":post_list, 
                                            "post_id":post_count,
                                            "page":page,
                                            "following":following,
                                            'paginator':paginator})
 
 
def post_view(request, username, post_id):
    user=get_object_or_404(User, username__iexact=username)
    username=user.username
    user_first_name=user.first_name
    user_last_name=user.last_name
    post=Post.objects.get(id=post_id)
    form=CommentForm(instance=None)
    post_count=Post.objects.filter(author=user).count()
    followers_count=Follow.objects.filter(author=user).count()
    followings_count=Follow.objects.filter(user=user).count()
    pub_date=post.pub_date
    items=post.comments.all()
  
    
    return render(request, 'post.html', {"username":username, 
                                         "post_id":post_id, 
                                         "user_first_name":user_first_name, 
                                         "user_last_name":user_last_name, 
                                         "post_count":post_count, 
                                         "followers_count":followers_count,
                                         "followings_count":followings_count,
                                         "post":post, 
                                         "pub_date":pub_date,
                                         "form":form,
                                         "items":items})

@login_required
def post_edit(request, username, post_id):
    user=get_object_or_404(User, username__iexact=username)
    post=Post.objects.get(id=post_id)
    if user==post.author:
        if request.method=='POST':
            form=PostForm(request.POST or None, files=request.FILES or None, instance=post)
            if form.is_valid():
                post=form.save(commit=False)
                post.author=request.user
                post.save()
                return redirect('profile', username)
        form=PostForm(instance=post)
        return render(request, 'new.html', {"form":form,"user":user, "post":post})
    return redirect('post', username, post_id)

def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path':request.path}, status=404)

def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post=get_object_or_404(Post, pk=post_id, author__username=username)
    form=CommentForm(request.POST or None)
    items=Post.objects.all()
    if form.is_valid:
        comment=form.save(commit=False)
        comment.post=post
        comment.author=request.user
        comment.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "post.html", {"form":form, "post":post, "items":items})

@login_required
def follow_index(request):
    user_follows=User.objects.get(pk=request.user.id).follower.all().values_list('author')
    post_list=Post.objects.filter(author__in=user_follows)
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    
    return render(request, 'follow.html', {"page":page, "paginator":paginator})


@login_required
def profile_follow(request, username):
    author=get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        follower=Follow.objects.create(author=author, user=request.user)
        follower.save()
        return redirect('profile', username=username)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    author=get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        follower=Follow.objects.get(author=author, user=request.user)
        follower.delete()
        return redirect('profile', username=username)
    return redirect('profile', username=username)

