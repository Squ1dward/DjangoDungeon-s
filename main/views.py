from logging import exception

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
            response_from_gpt = get_gpt(message,chat_profile)
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
            new_message_from_gpt = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=get_gpt(None,chat_profile), postDate=timezone.now())
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
    chat_message = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=get_gpt(None,chat_profile), postDate=timezone.now())
    chat_message.save()
    return redirect('/')

def world_building(request):
    if request.method == 'POST':
        form = WorldBuildingFormular(request.POST)
        if form.is_valid():
            print(form.cleaned_data['name'])
            print(form.cleaned_data['rasse'])
            print(form.cleaned_data['geschlecht'])
            print(form.cleaned_data['kampf'])
            print(form.cleaned_data)

            # Hier rufst du get_gpt mit den Formulardaten auf
            response = get_gpt_temp(form_data=form.cleaned_data)
            # Rest der Logik...
            return redirect('/')
    else:
        form = WorldBuildingFormular()

    return render(request, 'main/world_building.html', {'form': form})


def get_gpt_temp(form_data=None, user_prompt=None):
    """
    Generiert einen Prompt für den GPT-Dienst.

    Args:
        form_data (dict, optional): Die Formulardaten
        user_prompt (str, optional): Ein vordefinierter Prompt
    """
    if user_prompt is None and form_data is not None:
        user_data = ", ".join(f"{key}: {value}" for key, value in form_data.items())
        user_prompt = "You're a DungeonMaster, you create a dungeon scenario and I'm the main character. You start the story. Send also another text summarizing in words what you wrote. The player has given the following: " + user_data
    elif user_prompt is None:
        user_prompt = "You're a DungeonMaster, you create a dungeon scenario and I'm the main character. You start the story."

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
            "X-Title": "<YOUR_SITE_NAME>",  # Optional
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


def get_gpt(user_prompt, chat_profile):
    if user_prompt is None:
        user_prompt = "You're a DungeonMaster, you create a dungeon scenario and I'm the main character. You start the story, but please not too long responses"

    model_name = "cognitivecomputations/dolphin3.0-mistral-24b:free"

    if not model_name.__contains__(":free"):
        raise Exception("This AI model is not free, I don't want to pay for tokens >:(")
    else:
        # Prepare the messages for the API call
        messages = []
        if chat_profile.jsonText:
            messages = json.loads(chat_profile.jsonText)

        messages.append({
            "role": "user",
            "content": user_prompt
        })

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            },
            data=json.dumps({
                "model": model_name,
                "messages": messages,
            })
        )

        response_data = response.json()
        assistant_response = response_data['choices'][0]['message']['content']

        # Update the chat history
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Keep only the initial user message and the last 5 interactions
        initial_message = messages[0]
        if len(messages) > 11:  # 1 initial message + 5 pairs of user-assistant messages
            messages = [initial_message] + messages[3:]

        chat_profile.jsonText = json.dumps(messages)
        chat_profile.save()

    return assistant_response
