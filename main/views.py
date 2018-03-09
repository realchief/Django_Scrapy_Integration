# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.template import Context
from django.conf import settings
from django.http import HttpResponseRedirect

from .forms import DocumentForm
from .models import Document
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

# def Upload(request):
#     if not request.user.is_authenticated():
#         return redirect('main:login')
#
#     return render(request, 'pages/upload.html')


def Upload(request):
    if not request.user.is_authenticated():
        return redirect('main:login')

    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return redirect('main:upload')
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'pages/upload.html',
        {'documents': documents, 'form': form}
    )