from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return HttpResponse("Welcome to NigeriaSafe!")

def about(request):
    return HttpResponse("This is the About page of NigeriaSafe.")