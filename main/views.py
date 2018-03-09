# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.template import Context
from django.conf import settings

from .forms import LoginForm


def login(request):
    redirect_to = request.POST.get('next_',
                                   request.GET.get('next', 'main:upload'))
    if request.user.is_authenticated():
        return redirect(redirect_to)
    if request.method == "POST":

        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # Okay, security check complete. Log the user in.
            auth.login(request, form.get_user())
            return redirect(redirect_to)
    else:
        form = LoginForm(request, initial={'next_': redirect_to})

    return render(request, 'auth/login.html', {'form': form})


def logout(request):
    auth.logout(request)
    return redirect('main:login')


def Upload(request):
    if not request.user.is_authenticated():
        return redirect('main:login')


    return render(request, 'pages/upload.html')