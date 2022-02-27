
# import time

# from PlaxisTask.models import PlaxisTask
# from getPlaxisResults import getPlaxisResults

# class PlaxisRequest ():
#     def __init__(self) -> None:
#         pass
#     async def start (self, data):
#         pt = PlaxisTask(host=data.host, port=data.port, password=data.password, user=data.user,request=data.request)
#         pt.createdDT = time.Now()
#         pt.save
#         pr = getPlaxisResults(pt.host, pt.port, pt.password)
#         pt.result = await pr.getResults(pt.request);
#         pt.endDateTime 
#         pt.save

# https://stackoverflow.com/questions/6791911/execute-code-when-django-starts-once-only
# class PlaxisRequests:

#     def start (self):
#         self.requests = []
#         self.interrupt = False

#         self.add_and_remove_jobs(20);
     
#     def add_new_jobs(self) :
#         # https://docs.djangoproject.com/en/4.0/topics/db/queries/
#         new_jobs = PlaxisTask.objects.all.filter(startedDT is None) 
#         for pt in new_jobs:
#             pr = getPlaxisResults(host=pt.host, password=pt.password, taskid=pt.id)
#             pr.getResults(pt.request)
#             self.requests.append(pr)
#             pt.startedDT = time.Now()
#             pt.save
#     def all_requests_where(self, **kwargs):
#         return list(self.__iterrequests(**kwargs))
#     def __iterrequests(self, **kwargs):
#         # https://stackoverflow.com/questions/5180092/how-to-select-an-object-from-a-list-of-objects-by-its-attribute-in-python/5180993
#         return (request for request in self.requests if request.match(**kwargs))
        
#     def add_and_remove_jobs (self, wait):
#         while (self.interrupt == False) {
#             self.add_new_jobs
#             self.remove_completed_jobs
#             time.sleep(wait)  
#         }
    
#     def remove_completed_jobs (self):
#         completed_jobs = self.all_requests_where(result != '')
#         for pr in completed_jobs:
#            pt = PlaxisTask.objects.all.filter(id==pr.taskid)
#            pt.result = pr.result
#            pt.endedDT = time.Now()
#            pt.save               
#            self.requests.remove(taskid=pt.id)
    
#     def stop (self):
#         self.interrupt = True

