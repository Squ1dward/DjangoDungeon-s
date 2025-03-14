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
            response_from_gpt = get_gpt(message,None,chat_profile)
            chat_message_from_gpt = ChatMessage(profileId=chat_profile, userId_id=0, message=response_from_gpt, postDate=timezone.now())
            chat_message_from_gpt.save()
            chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
            chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id).values()
            form = ChatForm()
            messages_dict = {
                'messages': chat_messages,
                'form': form
            }
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
            #chat_profile = ChatProfile.objects.get(createdBy=user)
            #new_message_from_gpt = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=get_gpt(None,chat_profile), postDate=timezone.now())
            #new_message_from_gpt.save()
            return redirect('building')
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
    chat_profile.jsonText = ""
    chat_profile.save()
    return redirect('building')
    #chat_message = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=get_gpt(None,chat_profile), postDate=timezone.now())
    #chat_message.save()
    #return redirect('')

def world_building(request):
    if request.method == 'POST':
        form = WorldBuildingFormular(request.POST)
        if form.is_valid():
            #{'name': 'Test', 'race': 'dumbass', 'genre': 'unknown', 'weapon': 'lance', 'char_desc': 'a', 'world_desc': 'b'}
            print(form.cleaned_data)
            chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
            chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id)
            # Hier rufst du story_builder mit den Formulardaten und baust du deiner Welt.
            story = story_builder(form.cleaned_data)
            # Dann DungeonMaster antwortet zurück
            message = get_gpt(None,story,chat_profile)
            chat_message = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message=message, postDate=timezone.now())
            chat_message.save()
            #response = get_gpt_temp(form_data=form.cleaned_data)
            # Rest der Logik...
            return redirect('/')
    else:
        form = WorldBuildingFormular()

    return render(request, 'main/world_building.html', {'form': form})

def get_gpt(user_prompt, build_story, chat_profile):
    messages = []
    if build_story is not None:
        system_prompt = "You're a DungeonMaster, you create a dungeon scenario and I'm the main character. " + build_story + " Please use only the information i give to you"
        print(system_prompt)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    if user_prompt is None:
        user_prompt = "create and start the story now"

    model_name = "cognitivecomputations/dolphin3.0-mistral-24b:free"

    if not model_name.__contains__(":free"):
        raise Exception("This AI model is not free, I don't want to pay for tokens >:(")
    else:
        # Prepare the messages for the API call
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


def story_builder(form_data=None):
    if form_data is None:
        return redirect("building")

    default = "choose by yourself"
    name = form_data['name']
    if name == "":
        name = default
    race = form_data['race']
    if race == "":
        race = default
    genre = form_data['genre']
    if genre == "":
        genre = default
    weapon = form_data['weapon']
    if weapon == "":
        weapon = default
    char_desc = form_data['char_desc']
    if char_desc == "":
        char_desc = default
    world_desc = form_data['world_desc']
    if world_desc == "":
        world_desc = default

    final_msg = ("You build the story maked by player: (character name:" + name +
                 ", race: " + race +
                 ", genre: " + genre +
                 ", weapon using: " + weapon +
                 ", more character description: " + char_desc +
                 ", world description: " + world_desc + ").")
    return final_msg
