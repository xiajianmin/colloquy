'''
Created on Mar 11, 2013

@author: ACHIRA
'''
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render

def indexView(request): 
    return render(request, 'main/index.html')

def logoutView(request):
    logout(request)
    return HttpResponseRedirect('/')