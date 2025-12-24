from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return HttpResponse(request, 'home.html')

def about(request):
    return HttpResponse(request, 'about page')