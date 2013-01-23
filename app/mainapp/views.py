from django.http import  HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth


def home(request):
    return render(request, 'index.html')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
