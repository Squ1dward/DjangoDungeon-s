from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.views.generic import TemplateView


# Create your views here.

def index(request):
    return HttpResponse("",loader.get_template("polls/index.html"))

