from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import User, ChatProfile, ChatMessage, Chat

from django.views.generic import TemplateView


# Create your views here.

def index(request):
    messages_dict = {}
    model = User.objects.all()
    template = loader.get_template("main/index.html")
    context = {}
    if request.user.is_authenticated:
        chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
        chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id).values()
        messages_dict = {
            'messages': chat_messages,
        }
    return HttpResponse(template.render(messages_dict, request))

def stats(request):
    model = User.objects.all()
    template = loader.get_template("main/stats.html")
    context = {}
    return HttpResponse(template.render(context, request))
