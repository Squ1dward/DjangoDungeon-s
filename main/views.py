from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

from .models import User, ChatProfile, ChatMessage
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, ChatForm

from django.views.generic import TemplateView


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
            # TODO: Armin soll hier seinem GPT-Prompt coden. Der Antwort unter chat_message_from_gpt -> message='{{Hier dein GPT-Antwort eingeben}}' implementieren
            # -> Get response from GPT
            #response_from_gpt = '{{Hier dein GPT-Antwort eingeben}}'
            #chat_message_from_gpt = ChatMessage(profileId=chat_profile.id, userId_id=0, message=response_from_gpt, postDate=timezone.now())
            #chat_message_from_gpt.save()
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

def logout_view(request):
    logout(request)
    return redirect('/')

def delete_chat_view(request):
    chat_profile = ChatProfile.objects.get(createdBy=request.user.id)
    chat_messages = ChatMessage.objects.filter(profileId=chat_profile.id)
    for chat_message in chat_messages:
        chat_message.delete()
    chat_message = ChatMessage(profileId=chat_profile, userId=User.objects.get(id=0), message="You need to save the village from evil goblins, they choose you as the only one goblin-hunter. You need to defeat the goblin-chief. Do you want to join the adventure?", postDate=timezone.now())
    chat_message.save()
    return redirect('/')