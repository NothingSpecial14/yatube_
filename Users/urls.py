from django.urls import path
from . import views

urlpatterns=[
    path('signup/', views.SignUp.as_view(), name="signup"),
    path('new/', views.new_post, name='new_post'),
    
]