# https://stackoverflow.com/questions/17601698/can-you-perform-multi-threaded-tasks-within-django
from django.http import HttpResponse, JsonResponse
import threading
from .models import Crawl

def startCrawl(request):
    task = Crawl()
    task.save()
    t = threading.Thread(target=doCrawl,args=[task.id])
    t.setDaemon(True)
    t.start()
    return JsonResponse({'id':task.id})

def checkCrawl(request,id):
    task = Crawl.objects.get(pk=id)
    return JsonResponse({'is_done':task.is_done, 'result':task.result})

def doCrawl(id):
    task = Crawl.objects.get(pk=id)
    # Do crawling, etc.

    task.result = result
    task.is_done = True
    task.save()