from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import Paginator

from .azure_controller import upload_file_to_blob, download_a_blob, delete_a_blob, list_blobs
from azure.storage.blob import BlobServiceClient
from .models import UpFile


def index(request):
    return render (request, 'Files/index.html')

def list_files(request):
    blob_service_client = BlobServiceClient.from_connection_string(settings.CONNECTION_STRING)
    container_name=settings.CONTAINER_NAME
    container_client=blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    blob_name_list=[]
    for blob in blob_list:
        blob_name = blob.name
        blob_name_list.append(blob_name)
    paginator = Paginator(blob_name_list, 10)  #Change number of items per page to a higher number (10? 20?)
    page = request.GET.get('page') 
    blob_name_list = paginator.get_page(page)
    #search bar:
    file_objects=UpFile.objects.all()
    # item_name = request.GET.get('item_name')
    # if item_name != '' and item_name is not None:
    #     file_objects = file_objects.filter(file_name__icontains=item_name)
    #     return file_objects

    return render(request, 'Files/list_files.html', {'blob_name_list': blob_name_list,  "file_objects":file_objects})


def upload_file(request):
    if request.method == "POST": 
        files = request.FILES.getlist('files')
        for file in files:
            file_name = file.name
            upload_file_to_blob(file, file_name) 
            messages.success(request, "Your file was successfully uploaded")   
    return render(request, 'Files/upload_file.html', {})


def delete_file(request,blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(settings.CONNECTION_STRING)
    container_name=settings.CONTAINER_NAME
    container_client=blob_service_client.get_container_client(container_name)
    blob_list=list_blobs()
    for blob in blob_list:
        blob_name = blob.name
    delete_a_blob(blob_name)
    list_blobs()
    return render(request,'Files/delete_file.html', {"blob_list":blob_list})   #(request,"files/delete_file.html", {'file_id': file_id})


def download_file(request, blob_name):
    blob_content = download_a_blob(blob_name)
    if blob_content:
        response = HttpResponse(blob_content.readall())
        response['Content-Disposition'] = f'attachment; filename={blob_name}'
        messages.success(request, "Your file was successfully downloaded")
        return response
    return render(request, 'Files/list_files.html', {})

        

   


    



 

