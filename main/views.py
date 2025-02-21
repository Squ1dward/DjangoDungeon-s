from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import User, ChatProfile, ChatMessage, Chat

from django.views.generic import TemplateView


# Create your views here.

def index(request):
    model = User.objects.all()
    template = loader.get_template("main/index.html")
    #chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
    #chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id)
    #context = {chat_profile, chat_messages}
    context = {}
    return HttpResponse(template.render(context, request))

def stats(request):
    model = User.objects.all()
    template = loader.get_template("main/stats.html")
    context = {}
    return HttpResponse(template.render(context, request))
