from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('send-message/', views.send_message_to_other, name='send_message_to_other'),
    path('<str:username>/', login_required(views.chat_user),name="chat_user"),

]
