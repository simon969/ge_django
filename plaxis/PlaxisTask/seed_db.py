from plaxis.PlaxisTask.models import PlaxisTask
from plaxis.PlaxisTask.serializers import PlaxisTaskSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

plaxis = PlaxisTask(host=r'UKCRD1PC40320', password=r'%4eRDYh7B@/EVx>X', request='All Structural', phases='Phase1,Phase2,Phase3')
plaxis.save()

plaxis = PlaxisTask(host=r'UKCRD1PC40320',password=r'%4eRDYh7B@/EVx>X', request='Plates', phases='Phase1,Phase2,Phase3' )
plaxis.save()

plaxis = PlaxisTask(host=r'UKCRD1PC40002',password='', request='Plates', phases='Phase1,Phase2,Phase3' )
plaxis.save()