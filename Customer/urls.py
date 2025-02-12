from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('', login_required(views.IndexView.as_view()),name="home"),
]
