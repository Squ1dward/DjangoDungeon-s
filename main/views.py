from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

from .models import User, ChatProfile, ChatMessage
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, ChatForm, RegisterForm
from django import forms

# views.py
from django.shortcuts import render
from .forms import WorldBuildingFormular

from django.views.generic import TemplateView
import requests
import json





# Create your views here.

def index(request):
    messages_dict = {}
    model = User.objects.all()
    chat_profile = None
    chat_messages = None
    template = loader.get_template("main/index.html")
    context = {}
    if request.user.is_authenticated:
        chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
        chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id).values()
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            # Get message sended by player
            message = form.cleaned_data['text_field']
            chat_message = ChatMessage(profileId=chat_profile, userId_id=request.user.id, message=message, postDate=timezone.now())
            chat_message.save()
            # -> Get response from GPT
            response_from_gpt = get_gpt(message)
            chat_message_from_gpt = ChatMessage(profileId=chat_profile, userId_id=0, message=response_from_gpt, postDate=timezone.now())
            chat_message_from_gpt.save()
            chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
            chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id).values()
            messages_dict = {
                'messages': chat_messages,
                'form': form
            }
            form = ChatForm()
            return HttpResponse(template.render(messages_dict, request))
    else:
        form = ChatForm()
        messages_dict = {
            'messages': chat_messages,
            'form': form
        }
    return HttpResponse(template.render(messages_dict, request))

def stats(request):
    model = User.objects.all()
    template = loader.get_template("main/stats.html")
    context = {}
    return HttpResponse(template.render(context, request))


def login_view(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect to a homepage or other page
            else:
                error_message = 'Benutzername oder Password ist falsch!'
    else:
        form = LoginForm()

    return render(request, 'main/login_view.html', {'form': form, 'error_message': error_message})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            new_chat_profile = ChatProfile(creationDate=timezone.now(), createdBy=user)
            new_chat_profile.save()
            chat_profile = ChatProfile.objects.get(createdBy=user)
            new_message_from_gpt = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=get_gpt(None), postDate=timezone.now())
            new_message_from_gpt.save()
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def delete_chat_view(request):
    chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
    chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id)
    for chat_message in chat_messages:
        chat_message.delete()
    chat_message = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=get_gpt(None), postDate=timezone.now())
    chat_message.save()
    return redirect('/')

def world_building(request):
    if request.method == 'POST':
        form = WorldBuildingFormular(request.POST)
        if form.is_valid():
            print(form.cleaned_data)  # Hier kannst du z.B. speichern oder weitergeben
    else:
        form = WorldBuildingFormular()

    return render(request, 'main/world_building.html', {'form': form})

# Hier wird text hinzugefügt für charer erstelung
def get_gpt(user_prompt):
    if user_prompt is None:
        user_prompt = "You're a DungeonMaster, you create an dungeon scenario and I'm the main character. You start the story. Send also another text summaring in words what you wrote. The player has chosen these criteria ... and has written the story for himself ... and has written the following story for the world ..."
    response = requests.post(
      url="https://openrouter.ai/api/v1/chat/completions",
      headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
      },
      data=json.dumps({
        "model": "cognitivecomputations/dolphin3.0-mistral-24b:free",
        "messages": [
          {
            "role": "user",
            "content": user_prompt
          }
        ],

      })
    )
    response_data = response.json()
    first_response = response_data['choices'][0]['message']['content']
    return first_response

