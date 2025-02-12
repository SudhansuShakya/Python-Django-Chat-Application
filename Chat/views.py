from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse

from django.contrib import messages
from django.contrib.auth.models import User
# from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.db.models import Q

from .models import Message


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count
from django.db.models.functions import TruncDate



def chat_user(request,username):
    user1 = request.user
    user2 = get_object_or_404(User,username=username)
    messages=Message.objects.filter(
            (Q(sender=user1) & Q(recipient=user2)) |(Q(sender=user2) & Q(recipient=user1))).order_by('timestamp').annotate(date_only=TruncDate('timestamp'))
    # Group messages by date
    grouped_messages = {}
    for message in messages:
        message_date = message.date_only
        if message_date not in grouped_messages:
            grouped_messages[message_date] = []
        grouped_messages[message_date].append(message)
       
    context={
        'user':user2,
        'customers':User.objects.all(),
        'grouped_messages':grouped_messages
        # 'messages':Message.objects.filter(
        #     (Q(sender=user1) & Q(recipient=user2)) |(Q(sender=user2) & Q(recipient=user1))).order_by('timestamp')
    }
    return render(request,'chat_user.html',context)

import json
from datetime import datetime

def send_message_to_other(request):
    if request.method == 'POST':
        msg=request.POST['msg']
        receiver=User.objects.get(id=int(request.POST['receiver']))
        messageObj=Message.objects.create(sender=request.user,recipient=receiver,content=msg)
        if messageObj:
            channel_layer = get_channel_layer()
            user_id=receiver.id
            message=msg
            async_to_sync(channel_layer.group_send)(
                f'notifications_{user_id}',
                {
                    'type':'receive',
                    'message':message,
                    'time':str(messageObj.timestamp),
                    'sender':request.user.username,
                }
            )
        context={
            'success': 'Form successfully submitted',
            'message':message,
            'time':str(messageObj.timestamp),
            'sender':request.user.username,
        }
        return JsonResponse(context)
        # else:
        #     return JsonResponse({'error': 'Form is not valid'})
    
    else:
        user=User.objects.get(username=user)
        messages=Message.objects.filter(
                (Q(sender=user1) & Q(recipient=user2)) |(Q(sender=user2) & Q(recipient=user1))).annotate(date_only=TruncDate('timestamp'))
        # Group messages by date
        grouped_messages = {}
        for message in messages:
            message_date = message.date_only
            if message_date not in grouped_messages:
                grouped_messages[message_date] = []
            grouped_messages[message_date].append(message)
       
        context={
            'user':user,
            'customers':User.objects.all(),
            'grouped_messages':grouped_messages
        }
        return render(request,'chat_user.html',context)
    



