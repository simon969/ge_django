import threading
import os
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from ge_py.quickstart.models import NOT_INTEGER, get_integer

from ags.AGSTask.serializers import AGSTaskViewSetSerializer
from ags.AGSTask.models import AGSDocuments, AGSTask, get_task_results

# Create your views here.

class AGSTaskViewSet(ModelViewSet):
    queryset =  AGSTask.objects.all()
    serializer_class = AGSTaskViewSetSerializer
    permissions_classes =  (IsAuthenticated,)
    # http_method_names = ['post','get']
    
    @csrf_exempt
    def list(self, request):
        """
        list ags tasks.
        """
        if request.method == 'GET':
            plaxis = self.get_queryset()
            serializer = AGSTaskViewSetSerializer(plaxis, many=True)
            return JsonResponse(serializer.data, safe=False)
         
    @csrf_exempt
    def detail(self, request, pk):
        """
        Retrieve, update or delete a plaxis task.
        """
        print ("detail:",request.method)
        try:
            task = AGSTask.objects.get(pk=pk)
        except AGSTask.DoesNotExist:
            return HttpResponse(status=404)

        if request.method == 'GET':
            serializer = AGSTaskViewSetSerializer(task)
            return JsonResponse(serializer.data)

        elif request.method == 'PUT':
            data = JSONParser().parse(request)
            serializer = AGSTaskViewSetSerializer(task, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)

        elif request.method == 'DELETE':
            task.delete()
            return HttpResponse(status=204)

    def get_queryset(self):
        """
        Restricts the returned tasks to a given owner,
        by filtering against an owner query parameter in the URL or the query_params
        """
        queryset = AGSTask.objects.all()
        owner = self.request.query_params.get('owner')
        if owner is None and 'owner' in self.kwargs:
            owner = self.kwargs['owner']
        if owner is not None:
            queryset = queryset.filter(owner=owner)
        return queryset
    
    def create (self, request,*args,**kwargs):
        documents = request.FILES.getlist('files', None)
        data = {
            "task": request.POST.get('task', None),
            "owner": request.POST.get('owner', None)
        }
        _serializer = self.serializer_class (data=data,context={'documents':documents})
        if _serializer.is_valid():
            task = _serializer.save()
            self.start_task (request, task.id)
            return JsonResponse(data=_serializer.data,status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, *args, **kwargs):
        """
        Download the results of a AGS task  
        if 'element' is in kwargs and its an integer its used directly for the records in the AGSDocuments associated with the AGSTask, 
        if it's a string then the offset is looked up from the file name and if is not provided at all then the first AGSDocument is returned

        """
        # https://django.readthedocs.io/en/stable/howto/outputting-csv.html
        
        try:
            pk = kwargs['pk']
            task = AGSTask.objects.get(pk=pk)
            docs = AGSDocuments.objects.filter(task_id=pk)

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
        except:
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
        start the ags task (get_task_results) in a new thread

        """
        try:
            task = AGSTask.objects.get(pk=pk)
        except AGSTask.DoesNotExist:
           return
        
        _serializer = self.serializer_class(task)

        t = threading.Thread(target=get_task_results,args=[pk])
        t.setDaemon(True)
        t.start()
        
        return JsonResponse(data=_serializer.data,status=status.HTTP_202_ACCEPTED)  
class AGSTaskOwnerList(generics.ListAPIView):
    serializer_class = AGSTaskViewSetSerializer

    def get_queryset(self):
        """
        Restricts the returned tasks to a given owner,
        by filtering against an owner query parameter in the URL or the query_params
        """
        queryset = AGSTask.objects.all()
        owner = self.request.query_params.get('owner')
        if owner is None and 'owner' in self.kwargs:
            owner = self.kwargs['owner']
        if owner is not None:
            queryset = queryset.filter(owner=owner)
        return queryset