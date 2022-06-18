

import os
import uuid
import json
from datetime import datetime
import pytz
import string
import random
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from django.core.files.base import ContentFile
from rest_framework import status
from ge_py.quickstart.models import split_trim

from plaxis.PlaxisRequests.getPlaxisResults import Plaxis2dResultsConnectV2
from plaxis.PlaxisRequests.getPlaxisResults import Plaxis3dResultsConnect

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])

TRUE = 1

class Status:
        FAIL = -1
        READY = 0
        PROCESSING = 1
        SUCCESS = 2

def task_doc_path (instance, filename):
    return 'plaxis/documents/{0}/{1}'.format(str(instance.task.id)[:8], filename)

class PlaxisTask (models.Model):
    id = models.UUIDField(
         primary_key = True,
         default = uuid.uuid4,
         editable = False)
    conn = models.JSONField(blank=False, default=dict)
    query =models.JSONField(blank=False, default=dict)
    files = models.TextField(blank=True)
    result = models.TextField(blank=True)
    is_connected =  models.BooleanField (default=False)
    createdDT = models.DateTimeField(auto_now_add=True)
    completedDT = models.DateTimeField(null=True)
    status = models.IntegerField(null=False, default = 0)
    progress = models.TextField()
    owner =  models.CharField(max_length=100, blank=False)
  
    class Meta:
      ordering = ['createdDT']
    def progress_add (self, msg):
        if (msg is None):
            return
        self.progress += "{0}:{1}".format(datetime.now(), msg + '/r/n')

class PlaxisDocuments (models.Model):
    id = models.UUIDField(
         primary_key = True,
         default = uuid.uuid4,
         editable = False)
    task = models.ForeignKey(PlaxisTask, related_name="taskfiles", on_delete=models.CASCADE) #NOQA

    document = models.FileField (upload_to=task_doc_path, null=True,blank=True)
    ## document = models.FileField (upload_to='plaxis/documents/%Y/%m/%d/',null=True, blank=True)

def get_task_files (pk):
     
     """
     return a comma separated list of filenames associated with this task id
     """
     
     task_docs = PlaxisDocuments.objects.filter(task_id=pk)
     if task_docs is None:
               return
     files = []
     for doc in task_docs:
          files.append(os.path.basename(doc.document.name))
     return  ",".join(files)
    
def get_tasks_connected(host, port):
        tasks = PlaxisTask.objects.filter(conn__icontains=host)
        tasks = tasks.filter(conn__icontains=port)
        if (tasks.filter(is_connected__exact=True)):
            return tasks
        else:
            return None
        
def any_task_connected(host, port):
        tasks = PlaxisTask.objects.filter(conn__icontains=host)
        tasks = tasks.filter(conn__icontains=port)
        if (tasks.filter(is_connected__exact=True)):
            return True
        else:
            return False

def get_task_results(pk):

    """
    retrieve the plaxis task, run it and save results

    """
    try:
        task = PlaxisTask.objects.get(pk=pk)
    except PlaxisTask.DoesNotExist:
        return 

    try:
      
        query = json.loads(task.query.replace("'","\""))
        conn = json.loads(task.conn.replace("'","\""))

        version = query.get("version")

        host = conn["host"]
        port = conn["port"]

        if (any_task_connected(host, port) == True):
            task.progress_add ("Unable to complete ge_task_results for ({0}), host({1}) and port({2}) is in use by another task".format(pk, host, port))
            task.status = Status.READY
            task.is_connected = False
            task.save()
            return
        
        task.progress_add ("get_task_results() started")
        task.status = Status.PROCESSING
        task.save()

        password = conn["password"]
        filename =  query.get("filename")
        
        if filename is None:
            filename = "%host_%datetime_%random_%result.csv"

        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        dt_now =  datetime.now()
        filename = filename.replace("%random",rand)
        filename = filename.replace("%host",host)
        filename = filename.replace("%datetime", dt_now.strftime("%Y%m%d%H%M%S"))

        try:
            if (version == 'Plaxis2dConnectV2'):
                pr = Plaxis2dResultsConnectV2 (host=host, port=port, password=password)
            if (version == 'Plaxis2dConnect'):
                pr = Plaxis2dResultsConnectV2 (host=host, port=port, password=password)
            if (version == 'Plaxis3dConnect'):
                pr = Plaxis3dResultsConnect (host=host, port=port, password=password)
        except (TypeError, ValueError):
            pr = None

        if pr is None:
            task.progress_add (version + " unable to connect ")
            task.status = Status.READY
            task.is_connected = False
            task.save()
            return

        task.is_connected = pr.is_connected()
        task.progress_add ("{0}:{1} ({2}) connected:{3}".format(host, port, pr.version(), task.is_connected))
        task.save();        
    
        if (task.is_connected == False):
            return 

        elements = split_trim(query["results"])
        
        results = []    
        
        for element in elements:
            element_done = False
            if (element == 'Plates'):
                content = ContentFile (content='initilize file', name = filename.replace("result","plates"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getPlateResults (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None
                            )
                task.progress_add("Plate results retrieved")
                task.save()
                element_done = True
        
            if (element == 'EmbeddedBeams'):
                content = ContentFile (content='initilize file', name = filename.replace("result","embeddedbeams"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getEmbeddedBeamResults (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None
                            )
                task.progress_add("EmbeddedBeam results retrieved")
                task.save()
                element_done = True
            
            if (element == 'Interfaces'):
                content = ContentFile (content='initilize file', name = filename.replace("result","interfaces"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getInterfaceResults (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None
                            )
                        
                task.progress_add("Interfaces results retrieved")
                task.save()
                element_done = True
            
            if (element == 'FixedEndAnchors'):
                content = ContentFile (content='initilize file', name = filename.replace("result","fixedendanchors"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getFixedEndAnchorResults (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None
                            )
                        
                task.progress_add("FixedEndAnchor results retrieved")
                task.save()
                element_done = True
            
            if (element == 'NodeToNodeAnchors'):
                content = ContentFile (content='initilize file', name = filename.replace("result","nodetonodeanchors"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getNodeToNodeAnchorResults (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None
                            )
                task.progress_add("NodeToNodeAnchor results retrieved")
                task.save()
                element_done = True
            
            if (element == 'SoilResultsByPoints'):
                content = ContentFile (content='initilize file', name = filename.replace("result","soilbypoints"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getSoilResultsByPoints (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None
                            )
                task.progress_add("SoilResultsByPoints retrieved")
                task.save()
                element_done = True
            
            if (element == 'SoilResultsByRanges'):
                content = ContentFile (content='initilize file', name = filename.replace("result","soilbyranges"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getSoilResultsByRanges (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None,
                            xMin=None, xMax=None,
                            yMin=None, yMax=None,
                            )
                task.progress_add ("SoilResultsByRanges retrieved")
                task.save()
                element_done = True
            
            if (element == 'InterfaceResultsByPointsByStep'):
                content = ContentFile (content='initilize file', name = filename.replace("result","interfacebyrangesbystep"))
                file = PlaxisDocuments.objects.create(task=task, document=content)
                file.save() 
                result = pr.getInterfaceResultsByPointsByStep (fileOut=file.document.path, tableOut=None,
                            sphaseOrder=query["phases"],
                            sphaseStart=None,
                            sphaseEnd=None,
                            stepList=query["steps"]
                            )
                        
                results.append (result)
                task.progress_add ("InterfaceResultsByPointsByStep retrieved")
                task.save()
                element_done = True
            
            if (element_done == False):
                results.append (element + " not found")
                task.progress_add (element + " results not retrieved")
                task.save()

        task.files =  get_task_files(task.id)
        task.completedDT = datetime.now(pytz.UTC)
        task.is_connected = False
        task.progress_add ("get_task_results() completed")
        task.status = Status.READY
        task.save()
        return
    except Exception as e:
        print (getattr(e, 'message', repr(e)))
        task.progress_add (version + " " + getattr(e, 'message', repr(e)))
        task.is_connected = False
        task.status = Status.READY
        task.save()
        return