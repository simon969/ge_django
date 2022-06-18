import threading
import os
from datetime import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import action
from rest_framework.parsers import JSONParser

from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics

from ge_py.quickstart.models import NOT_INTEGER, get_integer

from plaxis.PlaxisTask.models import PlaxisTask, PlaxisDocuments, get_task_results, any_task_connected
from plaxis.PlaxisTask.serializers import PlaxisTaskSerializerCreate
from plaxis.PlaxisTask.serializers import PlaxisTaskSerializer



# Create your views here.

class PlaxisViewSet(ModelViewSet):
    """
    API endpoint that allows Plaxis results be viewed.
    """
    queryset = PlaxisTask.objects.all()
    serializer_class = PlaxisTaskSerializer
   # permission_classes = [permissions.IsAuthenticated]

# https://stackoverflow.com/questions/17601698/can-you-perform-multi-threaded-tasks-within-django
    def get_queryset(self):
        """
        Restricts the returned tasks to a given owner,
        by filtering against an owner query parameter in the URL or the query_params
        """
        queryset = PlaxisTask.objects.all()
        owner = self.request.query_params.get('owner')
        if owner is None and 'owner' in self.kwargs:
            owner = self.kwargs['owner']
        if owner is not None:
            queryset = queryset.filter(owner=owner)
        
        return queryset.order_by('-createdDT')

    @csrf_exempt
    def list(self, request):
        """
        list plaxis tasks.
        """
        if request.method == 'GET':
            plaxis = self.get_queryset()
            serializer = PlaxisTaskSerializer(plaxis, many=True)
            return JsonResponse(serializer.data, safe=False)
         
    @csrf_exempt
    def detail(self, request, pk):
        """
        Retrieve, update or delete a plaxis task.
        """
        print ("detail:",request.method)
        try:
            plaxis = PlaxisTask.objects.get(pk=pk)
        except PlaxisTask.DoesNotExist:
            return HttpResponse(status=404)

        if request.method == 'GET':
            serializer = PlaxisTaskSerializer(plaxis)
            return JsonResponse(serializer.data)

        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = PlaxisTaskSerializer(plaxis, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        elif request.method == 'DELETE':
            plaxis.delete()
            return HttpResponse(status=204)
    
    @csrf_exempt
    def create (self, request):
        """
        Create a plaxis task.
        """
        if request.method == 'POST':
            data = JSONParser().parse(request)
            serializer = PlaxisTaskSerializerCreate(data=data)
            if serializer.is_valid(): 
                if serializer.is_available(data):
                    task = serializer.create(data)
                    if (task):
                        return self.start_task (request, task.id)
                else:
                    msg  = "Unable to create new ge_task host is currently in use by another task"
                    return JsonResponse({'message': msg}, status=409)    
            else:
                return JsonResponse(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def download(self, request, *args, **kwargs):

        """
        Download the results of a Plaxis task  
        if 'element' is in kwargs and its an integer its used directly for the records in the PlaxisDocuments associated with the PlaxisTask, 
        if it's a string then the offset is looked up from the file name and if is not provided at all then the first PlaxisDocument is returned
        """

        # https://django.readthedocs.io/en/stable/howto/outputting-csv.html
        
        try:
            pk = kwargs['pk']
            task = PlaxisTask.objects.get(pk=pk)
            docs = PlaxisDocuments.objects.filter(task_id=pk)

            if task is None or docs is None:
                return HttpResponse(status=404)
        
        except Exception as e:
            print (getattr(e, 'message', repr(e)))
            return HttpResponse(status=404)
        
        try:
            element = kwargs.get('element',0)
            count = 0
            found = False
            element_integer = get_integer(element)
            # print(element, element_integer)
            for doc in docs:
                if element_integer == count:
                    found = True 
                    break
                if element_integer == NOT_INTEGER and element in doc.document.name:
                    found = True
                    break
                count += 1
            if not found:
                return HttpResponse(status=404)

        except Exception as e:
            print (getattr(e, 'message', repr(e)))
            return HttpResponse(status=404)
        
        # Create the HttpResponse object with the appropriate CSV header.
        try:
            with open(doc.document.path,'r') as file:
                response = HttpResponse(file.read(),content_type="text/csv")
                response['Content-Disposition'] = 'attachment; filename={0}'.format(os.path.basename(doc.document.name))
                return response
        except:
            return HttpResponse(status=404)
    
    @action(detail=True, methods=['get'])
    def start_task(self, request, pk):
        """
        start the plaxis task in a new thread

        """
        try:
            task = PlaxisTask.objects.get(pk=pk)
            serializer = PlaxisTaskSerializer(task)
            t = threading.Thread(target=get_task_results,args=[pk])
            t.setDaemon(True)
            t.start()
            return  JsonResponse(data = serializer.data, 
                                status=status.HTTP_202_ACCEPTED)

        except PlaxisTask.DoesNotExist:
            return HttpResponse(status=404) 

       

class PlaxisOwnerList(generics.ListAPIView):
    serializer_class = PlaxisTaskSerializer

    def get_queryset(self):
        """
        Restricts the returned tasks to a given owner,
        by filtering against an owner query parameter in the URL or the query_params
        """
        queryset = PlaxisTask.objects.all()
        owner = self.request.query_params.get('owner')
        if owner is None and 'owner' in self.kwargs:
            owner = self.kwargs['owner']
        if owner is not None:
            queryset = queryset.filter(owner=owner)
        
        return queryset