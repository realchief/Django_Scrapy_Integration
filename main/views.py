# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import auth
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.template import Context
from django.conf import settings
from django.http import HttpResponseRedirect

from .forms import DocumentForm
from .models import Document
from .forms import LoginForm

from uuid import uuid4
from urlparse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
from main.models import ScrapyItem
from scrapy_app.scraper.spiders import scrapingdata

import ContainerUI
import scrapy_app


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


# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True


@csrf_exempt
@require_http_methods(['POST', 'GET'])  # only get and post
def crawl(request):
    # Post requests are for new crawling tasks
    if request.method == 'POST':

        # url = request.POST.get('http://localhost:8000/api/crawl/')
        #
        # if not url:
        #     return JsonResponse({'error': 'Missing  args'})
        #
        # if not is_valid_url(url):
        #     return JsonResponse({'error': 'URL is invalid'})

        url = 'http://localhost:8000/api/crawl'

        domain = urlparse(url).netloc  # parse the url and extract the domain
        unique_id = str(uuid4())  # create a unique ID.

        # This is the custom settings for scrapy spider.

        settings = {
            'unique_id': unique_id,  # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        task = scrapyd.schedule('default', 'scrapingdata', settings=settings, url=url, domain=domain)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    # Get requests are for getting result of a specific crawling task
    elif request.method == 'GET':

        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                item = ScrapyItem.objects.get(unique_id=unique_id)
                return JsonResponse({'data': item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})
