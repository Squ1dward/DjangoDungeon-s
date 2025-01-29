from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import User

from django.views.generic import TemplateView


# Create your views here.

def index(request):
    model = User.objects.all()
    template = loader.get_template("main/index.html")
    context = {
        'numbers': {1,2,3,4,5,6,7,8,9,10},
    }
    return HttpResponse(template.render(context, request))

def stats(request):
    model = User.objects.all()
    template = loader.get_template("main/stats.html")
    context = {}
    return HttpResponse(template.render(context, request))
