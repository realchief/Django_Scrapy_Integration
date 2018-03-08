from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm


def handle_uploaded_file(f):
    with open('inputData.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'model_form_upload.html', {'form': form})