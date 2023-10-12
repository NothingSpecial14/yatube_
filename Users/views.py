from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy
from Users.forms import CreationForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from posts.models import Post

class SignUp(CreateView):
    form_class=CreationForm
    success_url=reverse_lazy("login")
    template_name="signup.html"

#jdef new_post(request):
    #form=PostForm()
    #return render(request, "new.html", {"form":form})
# Create your views here.
@login_required()
def new_post(request):
    if request.method=='POST':
        form=PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post=form.save(commit=False)
            post.author=request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html',{'form':form})
    form=PostForm()
    return render(request, 'new.html',{'form':form})


