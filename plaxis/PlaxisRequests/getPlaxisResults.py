#########################################################################
#
#      Title:       Plaxis 2d and Plaxis 3d Result Output Classes
#
#########################################################################
#
#      Description: Python classes to recover results from Plaxis 2d and Plaxis 3d analysis models
#
#               my_path = r'\\eu.aecomnet.com\euprojectvol\UKCRD1-TI\Projects\14\geotech1\GEO-3523'
#               my_module = imp.find_module('getPlaxisResults', [my_path])
#               getPlaxisResults = imp.load_module('getPlaxisResults', *my_module)
#
#
#
#               p2dr = getPlaxis2dResults(o_g)
#               p2dr.getSoilResultsByRange(
#                           fileOut=None,
#                           sphaseOrder=None,
#                           sphaseStart=None,
#                           sphaseEnd=None,
#                           xMin=None, xMax=None,
#                           yMin=None, yMax=None,
#                           )
#               p2dr.getPlateResults(
#                           fileOut=None,
#                           sphaseOrder=None,
#                           sphaseStart=None,
#                           sphaseEnd=None
#                           )
#               p2dr.getAllStructuralResults(
#                           fileOut=None,
#                           sphaseOrder=None,
#                           sphaseStart=None,
#                           sphaseEnd=None
#                           )
#
#               p3dr = getPlaxis3dResults(o_g)
#               p3dr.getSoilResultsByRange(
#                           fileOut=None,
#                           sphaseOrder=None,
#                           sphaseStart=None,
#                           sphaseEnd=None,
#                           xMin=None, xMax=None,
#                           yMin=None, yMax=None,
#                           )
#
#########################################################################
#
#########################################################################
#
#       Author      Thomson, Simon simon.thomson@aecom.com
#
##########################################################################
#
#       Version:    Beta 0.0.3
#
##########################################################################
#
#       Date:       2017 November 10
#
###########################################################################

##########################################################################
#
# Boiler Plate for project file  Plaxis 2D AE/2016
#
##########################################################################
#
#
# import imp
# plaxis_path = r'C:\Program Files (x86)\Plaxis\PLAXIS 2D'
# found_module = imp.find_module('plxscripting', [plaxis_path])
# plxscripting = imp.load_module('plxscripting', *found_module)
# from plxscripting.easy import *
#
# self.s_o, self.g_o = new_server('localhost', 10000)
#                  
##############################################################################

##########################################################################
#
# Boiler Plate for project file  Plaxis3D 2017
#
##########################################################################
#
#
# import imp
# plaxis_path = r'C:\Program Files\Plaxis\PLAXIS 3D\python\Lib\site-packages'
# found_module = imp.find_module('plxscripting', [plaxis_path])
# plxscripting = imp.load_module('plxscripting', *found_module)
# from plxscripting.easy import *
#
# self.s_o, self.g_o = new_server('localhost', port=10000, password='')   
#      
#
##############################################################################
import imp
import os.path
import math
import logging
import time
from io import StringIO

# path_croydon_ip = r'\\172.18.172.32\ukcrd1fp001-v1ti\Projects\14\geotech1\GEO-3523'
# path_croydon_vol= r'\\eu.aecomnet.com\euprojectvol\UKCRD1-TI\Projects\14\geotech1\GEO-3523'
# path_croydon_legacy_ip = r'\\172.18.172.14\local\Croydon\Legacy\UKCRD1FP001\UKCRD1FP001-V1TI\Projects\14\geotech1\GEO-3523'
# path_geo3523 = path_croydon_legacy_ip

# path_plaxis = path_geo3523  
# found_module = imp.find_module('plxscripting', [path_plaxis])
# plxscripting = imp.load_module('plxscripting', *found_module)

from plaxis.plxscripting.easy import new_server

from plaxis.pypyodbc import pypyodbc


# path_pypyodbc = path_geo3523 + r'\pypyodbc-1.3.5'
# found_module = imp.find_module('pypyodbc', [path_pypyodbc])
# pypyodbc = imp.load_module('pypyodbc', *found_module)

class PlaxisScripting (object):
    def __init__(self, server=None, host=None, port=None, password=None):
        
        hdlr = logging.FileHandler('PlaxisResults.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        
        self.logger = logging.getLogger('PlaxisResults')
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)
        print ('getting Connected...')      
        
        if server is None:
            if password is None:
                self.s_o, self.g_o = new_server(host, port, password='')
            else:
                self.s_o, self.g_o = new_server(host, port, password=password)
        else:
            self.g_o = server
        
        if (self.s_o.is_2d is False and self.s_o.is_3d is False ):
            print ('..no connection')     
            raise ValueError("Not Connected")
        else:
            print ('Connected:', host, port, self.s_o.name, self.s_o.major_version, self.s_o.minor_version, 'Is2d=', self.s_o.is_2d, 'Is3d=', self.s_o.is_3d)        

        self.NodeList = []
    def match(self, **kwargs):
        return all(getattr(self, key) == val for (key, val) in kwargs.items())     
    def connect (self, host, port, password):
        self.s_o, self.g_o = new_server(address=host, port=port, password=password)
        print ('Connected:', host, port, self.s_o.name, self.s_o.major_version, self.s_o.minor_version, 'Is2d=', self.s_o.is_2d, 'Is3d=', self.s_o.is_3d)
    def is_connected(self):
        if (self.s_o is not None):
            return True
        return False    
    def clearNodeList (self):    
        self.NodeList = []
    def printNodeListXYZ (self):
        formats =  '{},{:.3f},{:.3f},{:.3f}'
        for point in self.NodeList:
            print (formats.format(point.name, point.x, point.y, point.z))
            
           # print(point.name, point.x, point.y, point.z)
        
    class PointXY(object):
        def __init__(self, name, x, y):
                self.name = name
                self.x = float(x)
                self.y = float(y)
                self.coord = '{0:.3f},{1:.3f}'.format(float(x),float(y))
    class PointXYZ(object):
        def __init__(self, name, x, y, z):
                self.name = name
                self.x = float(x)
                self.y = float(y)
                self.z = float(z)
                self.coord = '{0:.3f},{1:.3f},{2:.3f}'.format(float(x),float(y),float(z))
    
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False  
    
    def isfloat(self, s, value_false):
        try:
            if s == 'NaN':
                return value_false
            if s == 'not found':
                return value_false
            else:
                f = float(s)
                print('float:', f)
                return f

        except ValueError:
            return value_false
    
    def getPhaseInt(self, 
                    phaseName):
        count = 0
        print('looking for phase:' + phaseName)
        for phase in self.g_o.Phases:
            if phase.Name.value == phaseName:
                print('found...', count)
                return count
            count += 1
        return -1
    def setSteps2(self, 
                 phase):
        
        self.Steps = []
        steps = phase[:]
        accessed_mapping = map(steps.__getitem__, self.StepList)
        self.Steps = list(accessed_mapping)
         
    def setSteps(self, 
                 phase):
        
        self.Steps = []
        
        print("{0} finding selected steps {1}".format(phase.Name.value,self.g_o.count(phase.Steps)))
        
        steps = phase[:]
        
        print ("{}".format(len(steps)))
 
        for step in steps:
            print ("{}".format(step))
            if not self.StepList or step in self.StepList:
                self.Steps.append(step)
                print("Added {0} {1}".format(step.Name, step))
        
    def setPhaseOrder(self,
                      sphaseOrder=None,
                      sphaseStart=None,
                      sphaseEnd=None):

        self.phaseOrder = []
        
        if sphaseOrder == 'All':
            sphaseOrder=None 
        
        if sphaseOrder is None:
            if sphaseStart is None and sphaseEnd is None:
                self.phaseOrder = self.g_o.Phases[:]
                if self.phaseOrder is not None:
                    print ('All phases added to phaseOrder')

            if sphaseStart is None and sphaseEnd is not None:
                id = self.getPhaseInt(sphaseEnd)
                self.phaseOrder = self.g_o.Phases[:id]
                if self.phaseOrder is not None:
                    print ('All phases up to', sphaseEnd, ' added')
    

            if sphaseStart is not None and sphaseEnd is None:
                id = self.getPhaseInt(phaseName=sphaseStart)
                self.phaseOrder = self.g_o.Phases[id:]
                if self.phaseOrder is not None:
                    print ('All phases from ', sphaseStart, ' added')

            if sphaseStart is not None and sphaseEnd is not None:
                id = self.getPhaseInt(sphaseStart)
                id2 = self.getPhaseInt(sphaseEnd)
                self.phaseOrder = self.g_o.Phases[id:id2 + 1]
                if self.phaseOrder is not None:
                    print ('All phases from ', sphaseStart, ' to ', sphaseEnd, ' added')
                    
        if sphaseOrder is not None:
            aphaseOrder = sphaseOrder.split(",")
            for sphase in aphaseOrder:
                id = self.getPhaseInt(sphase)
                self.phaseOrder.append(self.g_o.Phases[id])
                print('phase:', sphase ,' added')
        
        if self.phaseOrder is not None:
                    print ('phaseOrder initialised with', len(self.phaseOrder) , ' no. phases')   

                    
    def setRange (self,
                  xMin=None,
                  xMax=None,
                  yMin=None,
                  yMax=None,
                  zMin=None,
                  zMax=None
                  ):
        global g_xMin, g_xMax, g_yMin, g_yMax, g_zMin, g_zMax
        g_xMin = xMin
        g_xMax = xMax
        g_yMin = yMin
        g_yMax = yMax
        g_zMin = zMin
        g_zMax = zMax
        
    def printRange(self):
        print ('g_xMin',g_xMin, 
               'g_xMax',g_xMax,
               'g_yMin',g_yMin,
               'g_yMax',g_yMax,)
               
    def inRange (self,
                 x_val=None,
                 y_val=None,
                 z_val=None
                 ):
                 
        xMinRangeOk = True 
        xMaxRangeOk = True 
        yMinRangeOk = True
        yMaxRangeOk = True
        zMinRangeOk = True
        zMaxRangeOk = True
        
      #  self.printRange()
        
      #  print ('x_val', x_val,
      #        'y_val', y_val)
               
        if g_xMin is not None and x_val is not None:
            if x_val >= g_xMin:
                xMinRangeOk = True 
            else:
                xMinRangeOk = False  
        else:
            xMinRangeOk = True 
        
        if g_yMin is not None and y_val is not None:
            if y_val >= g_yMin:
                yMinRangeOk = True 
            else:
                yMinRangeOk = False
        else:
            yMinRangeOk = True 
        
        if g_xMax is not None and x_val is not None:
            if x_val <= g_xMax:
                xMaxRangeOk = True 
            else:
                xMaxRangeOk = False  
        else:
            xMaxRangeOk = True 
        
        if g_yMax is not None and y_val is not None:
            if y_val <= g_yMax:
                yMaxRangeOk = True 
            else:
                yMaxRangeOk = False
        else:
            yMaxRangeOk = True 
           
        if g_zMax is not None and z_val is not None:
            if z_val <= g_zMax:
                zMaxRangeOk = True 
            else:
                zMaxRangeOk = False
        else:
            zMaxRangeOk = True     
        
        if g_zMin is not None and z_val is not None:
            if z_val >= g_zMin:
                zMinRangeOk = True 
            else:
                zMinRangeOk = False
        else:
            zMinRangeOk = True 
            
        if xMinRangeOk and xMaxRangeOk and yMinRangeOk and yMaxRangeOk and zMinRangeOk and zMaxRangeOk:
           # print ('inRange x_val', x_val,
           #     'y_val', y_val)
            return True 
        else:
            return False  
            
    def setXYZNodeList (self,
                     xMin=0.0, xMax=0.0,
                     yMin=0.0, yMax=0.0,
                     zMin=0.0, zMax=0.0):
        
        phase = self.phaseOrder[0]
        count = 0
        
        self.setRange(xMin, xMax,
                      yMin, yMax, 
                      zMin, zMax)
        
        soilX = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.X, 'node')
        soilY = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Y, 'node')
        soilZ = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Z, 'node')
        
        print('Coordinates retrieved for Phase ', phase.Name.value)
        
        for x, y, z in zip(soilX, soilY, soilZ):
            if self.inRange (x_val = x, y_val = y, z_val = z) == True:
                count =  count + 1
                self.NodeList.append(self.PointXYZ(count, x, y, z))
                print ('Added node at (', x, y, z, ')')
        print (len(self.NodeList), ' nodes added to NodeList')
    
    def setXYZNodeList2 (self,
                     xMin=0.0, xMax=0.0,
                     yMin=0.0, yMax=0.0,
                     zMin=0.0, zMax=0.0):
        
        phase = self.phaseOrder[0]
        count = 0
        
        self.setRange(xMin, xMax,
                      yMin, yMax, 
                      zMin, zMax)
        soilN = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.NodeID, 'node')
        soilX = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.X, 'node')
        soilY = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Y, 'node')
        soilZ = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Z, 'node')
        
        print('Coordinates retrieved for Phase ', phase.Name.value)
        
        for x, y, z, n in zip(soilX, soilY, soilZ, soilN):
            if self.inRange (x_val = x, y_val = y, z_val = z) == True:
                count =  count + 1
                self.NodeList.append(self.PointXYZ(n, x, y, z))
                print ('Added node ',n,' at (', x, y, z, ')')
        print (len(self.NodeList), ' nodes added to NodeList')   
        
    def setXYNodeList (self,
                     xMin=0.0, xMax=0.0,
                     yMin=0.0, yMax=0.0):
        phase = self.phaseOrder[0]
        count = 0
        
        self.setRange(xMin, xMax,
                      yMin, yMax, 
                      zMin = None, zMax = None)
        
        soilX = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.X, 'node')
        soilY = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Y, 'node')
               
        print('Coordinates retrieved for Phase ', phase.Name.value)
        
        for x, y in zip(soilX, soilY):
            if self.inRange (x_val = x, y_val = y, z_val = None) == True:
                count =  count + 1
                self.NodeList.append(self.PointXY(count, x, y))
                print ('Added node at (', x, y, ')')
        print (len(self.NodeList), ' nodes added to NodeList')          
    def addXYNode(self, 
                    name,
                    x = 0.0, 
                    y = 0.0):
             
        self.NodeList.append(self.PointXY(name, x, y))
        print ('Added node at (',name, x, y, ')')
    
    def addXYZNode(self,
                    name,
                    x=0.0,
                    y=0.0,
                    z=0.0):
                
       
        self.NodeList.append(self.PointXYZ(name, x, y))
        print ('Added node at (',name, x, y, z, ')')
    
    def createXYArc(self,
                      name= None,
                      xCen= 0.00,
                      yCen= 0.00,
                      rad= 0.00,
                      degStart = 0.00,
                      degEnd = 0.00,
                      degStep = 0.00
                      ):
        ref = name
        count = 0
        arc_array = []
        
        x = 0.0
        y = 0.0
        
        arc_array = self.getArcCoordsArray(xCen,
                                      yCen,
                                      rad,
                                      degStart,
                                      degEnd,
                                      degStep)
        
        for coord in arc_array:
            x, y = coord
            self.NodeList.append(self.PointXY(name, x, y))
        print ('Added node at (',name, x, y, ')')    
    
    def createXYZArc_XYPlane(self,
                      name= None,
                      xCen= 0.00,
                      yCen= 0.00,
                      zCen= 0.00,
                      rad= 0.00,
                      degStart = 0.00,
                      degEnd = 0.00,
                      degStep = 0.00
                      ):
        ref = name
        count = 0
        arc_array = []
        
        x = 0.0
        z = 0.0
        
        arc_array = self.getArcCoordsArray(xCen,
                                      yCen,
                                      rad,
                                      degStart,
                                      degEnd,
                                      degStep)
        
        for coord in arc_array:
            x, y = coord
            self.NodeList.append(self.PointXYZ(name, x, y, zCen))
        print ('Added node at (',name, x, y, zCen, ')')
    
    def createXYZArc_XZPlane(self,
                      name= None,
                      xCen= 0.00,
                      yCen= 0.00,
                      zCen = 0.00,
                      rad= 0.00,
                      degStart = 0.00,
                      degEnd = 0.00,
                      degStep = 0.00
                      ):
        ref = name
        count = 0
        arc_array = []
        
        x = 0.0
        z = 0.0
        
        arc_array = self.getArcCoordsArray(xCen,
                                      zCen,
                                      rad,
                                      degStart,
                                      degEnd,
                                      degStep)
        
        for coord in arc_array:
            x, z = coord
            self.NodeList.append(self.PointXYZ(name, x, yCen, z))
        print ('Added node at (',name, x, yCen, z, ')')
    
    def createXYZArc_YZPlane(self,
                      name= None,
                      xCen= 0.00,
                      yCen= 0.00,
                      zCen = 0.00,
                      rad= 0.00,
                      degStart = 0.00,
                      degEnd = 0.00,
                      degStep = 0.00
                      ):
        ref = name
        count = 0
        arc_array = []
        
        y = 0.0
        z = 0.0
        
        arc_array = self.getArcCoordsArray(yCen,
                                      zCen,
                                      rad,
                                      degStart,
                                      degEnd,
                                      degStep)
        
        for coord in arc_array:
            y, z = coord
            self.NodeList.append(self.PointXYZ(name, xCen, y, z))
        print ('Added node at (',name, xCen, y, z, ')')    
    
    def getArcCoordsArray(self,
                      iCen= 0.00,
                      jCen= 0.00,
                      rad= 0.00,
                      degStart = 0.00,
                      degEnd = 0.00,
                      degStep = 0.00
                      ):
        i_coord = 0.0
        j_coord = 0.0
        coords = []                  
        
        # direction vector for 0 degree (j=1; i=0)
        # diection vector for 90 degree (j=0, i=1)
        
        deg = degStart
        
        while (deg < degEnd):
            i_coord  = iCen + rad * math.sin(math.radians(deg))
            j_coord =  jCen + rad * math.cos(math.radians(deg))
            coord = (i_coord, j_coord)  
            coords.append(coord)
            deg = deg + degStep
        return coords;
                          
    def createXYZCylinder(self,
                     name = None,
                     rad= 0.00,
                     degStart = 0.00,
                     degEnd = 0.00,
                     degStep = 0.00,
                     xMin= 0.0, xMax= 0.0, xStep= 0.0,
                     yMin= 0.0, yMax= 0.0, yStep= 0.0,
                     zMin= 0.0, zMax= 0.0, zStep= 0.0,
                     ):
       
        count = 0
        arc_coords = [] 
        x = 0.0
        y = 0.0
        z = 0.0
        
        if xStep == 0:
            xcount = 1
        else:
            xcount = int(abs((xMax - xMin) / xStep) + 0.1) + 1
        
        if yStep == 0:
            ycount = 1
        else:
            ycount = int(abs((yMax - yMin) / yStep) + 0.1) + 1
        
        if zStep == 0:
            zcount = 1
        else:
            zcount = int(abs((zMax - zMin) / zStep) + 0.1) + 1
        
        if (ycount == 1 and zcount == 1):
            # cyclinder direction in x axis, arc in zy plane
            arc_coords = self.getArcCoordsArray(yMin,zMin,rad,degStart,degEnd,degStep)
        
        if (xcount == 1 and zcount == 1):
            # cyclinder direction in y axis, arc in zx plane
            arc_coords = self.getArcCoordsArray(xMin,zMin,rad,degStart,degEnd,degStep)

        if (xcount == 1 and ycount == 1):
            # cyclinder direction in z axis, arc in xy plane
            arc_coords = self.getArcCoordsArray(xMin,yMin,rad,degStart,degEnd,degStep)
         
        for ix in range(0, xcount, 1):
            x = xMin + xStep * ix
            for iy in range (0, ycount, 1):
                y = yMin + yStep * iy
                for iz in range (0, zcount, 1):
                    z = zMin + zStep * iz
                    if (ycount == 1 and zcount == 1):
                        # cyclinder direction in x axis, arc in zy plane
                        for coord in arc_coords:
                            y_arc, z_arc = coord
                            self.NodeList.append(self.PointXYZ(name, x, y_arc, z_arc))   
                    
                    if (xcount == 1 and zcount == 1):
                        # cyclinder direction in y axis, arc in zx plane
                        for coord in arc_coords:
                            x_arc, z_arc = coord
                            self.NodeList.append(self.PointXYZ(name, x_arc, y, z_arc))    
                    
                    if (xcount == 1 and ycount == 1):
                        # cyclinder direction in z axis, arc in xy plane
                        for coord in arc_coords:
                            x_arc, y_arc = coord
                            self.NodeList.append(self.PointXYZ(name, x_arc, y_arc, z)) 
                    
    def getXYNodeListItem (self, x, y ):
        find_coord = "{0:.3f},{1:.3f}".format(float(x),float(y))
        for p in self.NodeList:
            # print (p.coord, find_coord)
            if (p.coord==find_coord):
                return p
        return None
        
    def createXYZGrid(self,
                      name=None,
                      xMin= 0.0, xMax= 0.0, xStep= 0.0,
                      yMin= 0.0, yMax= 0.0, yStep= 0.0,
                      zMin= 0.0, zMax= 0.0, zStep= 0.0,
                      ):
        
        ref = name
        count = 0
        
        x = 0.0
        y = 0.0
        z = 0.0
        
        if xStep==0:
            xcount = 1
        else:
            xcount = int(abs((xMax - xMin) / xStep) + 0.1) + 1
        
        if yStep==0:
            ycount = 1
        else:
            ycount = int(abs((yMax - yMin) / yStep) + 0.1) + 1
        
        if zStep==0:
            zcount = 1
        else:
            zcount = int(abs((zMax - zMin) / zStep) + 0.1) + 1
       
      #  print ('array size(', xcount, ycount, zcount, ')') 
        
        self.setRange(xMin, xMax,
                      yMin, yMax, 
                      zMin, zMax)
        
        for ix in range(0, xcount, 1):
            x = xMin + xStep * ix
            for iy in range (0, ycount, 1):
                y = yMin + yStep * iy
                for iz in range (0, zcount, 1):
                    z = zMin + zStep * iz
                    count = count + 1
                    if name is None:
                        ref = count
                    self.NodeList.append(self.PointXYZ(ref, x, y, z))
        #            print ('Added node at (', x, y, z, ')')            
                    
    def createXYGrid(self,
                      name=None,
                      xMin= 0.0, xMax= 0.0, xStep= 0.0,
                      yMin= 0.0, yMax= 0.0, yStep= 0.0):
                      
    
        count = 0
        ix = 0 
        iy = 0
        
        x = 0.0
        y = 0.0
        
        self.setRange(xMin, xMax,
                      yMin, yMax)
        if xStep==0:
            xcount = 1
        else:
            xcount = int(abs((xMax - xMin) / xStep) + 0.1) + 1
        
        if yStep==0:
            ycount = 1
        else:
            ycount = int(abs((yMax - yMin) / yStep) + 0.1) + 1
            
        for ix in range(1, xcount, 1):
            x = xMin + xStep * ix
            for iy in range (1, ycount, 1):
                y = yMin + yStep * iy
                count = count + 1
                if name is None:
                        ref = count
                self.NodeList.append(self.PointXY(ref, x, y))
                print ('Added node at (', x, y, ')') 
                
    def loadXYZNodeList (self, 
                      fileIn,
                      append = False):
    
        fpoint = open(fileIn, "r")
        
        if (append==False):
            self.NodeList = []
            
        while True:
            in_line = fpoint.readline()
            if in_line == "":
                break
            if ',' in in_line:
                [name, nx, ny, nz] = in_line.split(',')
                if self.is_number(nx):
                    if self.is_number(ny):
                        if self.is_number(nz):
                            self.NodeList.append(self.PointXYZ(name, nx, ny, nz))
                            print ('Node Added {},{:3f},{:3f},{:3f}'.format(name, float(nx), float(ny), float(nz)))

        fpoint.close()
    def loadXYNodeList (self, 
                      fileIn,
                      append = False):
    
        fpoint = open(fileIn, "r")
        
        if (append==False):
             self.NodeList = []
            
        while True:
            in_line = fpoint.readline()
            if in_line == "":
                break
            if ',' in in_line:
                [name, nx, ny] = in_line.split(',')
                if self.is_number(nx):
                    if self.is_number(ny):
                        self.NodeList.append(self.PointXY(name, nx, ny))
                        print ('Node Added {},{:3f},{:3f}'.format(name, float(nx), float(ny)))

        fpoint.close()
    def loadStepList(self,
                  fileIn,
                  append = False):
        fpoint = open(fileIn, "r")
        
        if (append==False):
             self.StepList = []
            
        while True:
            in_line = fpoint.readline()
            in_line = in_line.replace ('\n','')
            if in_line == "":
                break
            self.StepList.append(int(in_line))    
        
        fpoint.close()        
                
    def IsDbFile (self, db_file=None):   
        retvar = False
        
        if (db_file != None):
            if (db_file[-4:] == '.mdb'):
                retvar = True
            if (db_file[-6:] == '.accdb'):
                retvar = True
        
        return retvar
        
    def getConnected(self, db_file):
        
        self.conn_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + db_file + ';'
        
        file = ''
        
        if (os.path.isfile(db_file)):
            self.conn = pypyodbc.connect(self.conn_string)
            print('connecting to existing db:' + db_file)
        else:
            if db_file[-6:]=='.accdb':
                file = db_file[:-6]
            if db_file[-4:]=='.mdb':
                file = db_file[:-4]
            if not file:
                file = db_file
            self.conn = pypyodbc.win_create_mdb(file) 
            print('connecting to new db:' + db_file)
            db_file = file + '.mdb'
        
        self.db_file = db_file
        
        
    def setFields(self, fields, formats):
        self.columns = fields.split(',')
        self.formats = formats.split(',') 
        self.types = formats.split(',')
        for i in range(len(self.types)):
            if (self.formats[i]=='{:2f}'):
                self.types[i] = 'float'
            if (self.formats[i]=='{:f}'):
                self.types[i] = 'float'    
            if (self.formats[i]=='{}'):
                self.types[i] = 'varchar(255)'
            if (self.formats[i]=='{:0}'):
                self.types[i] = 'int'  
            if (self.formats[i]=='{0}'):
                self.types[i] = 'int'              
                    
    def createTable(self, tname, fields, formats):
        self.tname = tname
        self.setFields(fields, formats)
        self.sql_insert = 'insert into ' + tname + ' ('
        self.sql_drop = 'drop table ' + tname
        self.sql_create = 'create table '+ tname + ' (id autoincrement primary key, '
        self.sql_select = 'select '
        separator = ''
        for i in range (len(self.columns)):
            if (i > 0):
                separator=', '
            self.sql_create += separator + '[' + self.columns[i] + '] ' + self.types[i]
            self.sql_insert += separator + '[' + self.columns[i] + ']'
            self.sql_select += separator + '[' + self.columns[i] + ']'
        self.sql_create += ')'
        self.sql_insert += ')'
        self.sql_select += ' from ' + tname
        print (self.sql_create)
        cursor = self.conn.cursor()
        if (self.tableExists(tname)):
            cursor.execute(self.sql_drop)
        cursor.execute(self.sql_create) 
        self.conn.commit()
    def tableExists(self, tname):
        try:
            cursor = self.conn.cursor()
            sql = 'select top 1 * from '  + tname 
            cursor.execute(sql)
            return True
        except:
            return False
        
    def insertValues(self, data):
        self.sql_data = self.sql_insert + ' values ('  
        separator = ''
        for i in range(len(data)):
            if (i > 0):
                separator=', '
            if (self.types[i].find('varchar') >= 0):
                self.sql_data += separator + '\'' + str(data[i]) + '\'' 
            else:
                self.sql_data += separator +  str(data[i])
        self.sql_data += ')'
        cursor = self.conn.cursor()
        cursor.execute(self.sql_data)
        self.conn.commit()
            
class Plaxis3dInput (PlaxisScripting):
    def __init__(self,
                 input_server
                 ):
        super(Plaxis3dInput, self).__init__(input_server)  
        
#   file:///C:/Program%20Files/Plaxis/PLAXIS%203D/Manuals/English/input_objects/contents.html
    def getPhaseName(self, phase):
        for p in self.g_o.Phases[:]:
            if (str(p)==str(phase)):
                return p.Name
    
    def getPhaseDetails(self):
        results = []
        allpassed = True
        
        print('getting input phase details')
        
        for phase in self.g_o.Phases[:]:
            msg ="not calculated"
            if not phase.ShouldCalculate:
                if phase.CalculationResult == phase.CalculationResult.ok:
                    msg ="OK" 
                    #may be extended for more details
                else:
                    msg ="Failed: error {0}".format(phase.LogInfo)
                    allpassed =False
            
            prevPhaseName = self.getPhaseName (phase.PreviousPhase)
            results.append( "{},{},{},{},{},{}".format(phase.Name, phase.Comments, phase.Number, phase.Identification, prevPhaseName, phase.DeformCalcType))
        return allpassed, results

class Plaxis2dResults (PlaxisScripting):
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis2dResults, self).__init__(server, host, port, password=password)
       
        if (self.s_o.is_2d == False):
            raise ValueError('This is a Plaxis2d output reader, but the output plaxis server is not Plaxis2d');
    def version (self):
        return "Plaxis2d"    

    def getSoilResultsByRanges(self,
                              fileOut=None,
                              tableOut=None,
                              sphaseOrder=None,
                              sphaseStart=None,
                              sphaseEnd=None,
                              xMin=None, xMax=None,
                              yMin=None, yMax=None,
                              ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
                           
        self.setRange(xMin, xMax,
                      yMin, yMax)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByRanges'  

        locY = []
        locX = []
        
        Uyy = []
        Uxx = []
        Utot = []
        
        PUyy = []
        PUxx = []
        PUtot = []
        
        MaterialID = []
        ElementID =[]
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []        
        
        PExcess = []
        PActive = []
        PSteady = []
        PWater = []
        
        Suct = []
        EffSuct = []
        
        pPhaseName = []
        pPhaseIdent = []
        
        # look into all phases, all steps
        for phase in self.phaseOrder:
            print('Getting Soil results for Phase ', phase.Name.value, phase.Identification.value)
            
            soilMat = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.MaterialID, 'node')
            soilEl = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.ElementID, 'node')
            
            soilX = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.X, 'node')
            soilY = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Y, 'node')
            
            soilUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Ux, 'node')
            soilUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Uy, 'node')
            soilUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Ut, 'node')
            
            soilPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUy, 'node')
            soilPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUx, 'node')
            soilPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUt, 'node')            
            
            soilEffSxx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigxxE, 'node')
            soilEffSyy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigyyE, 'node')
            soilEffSzz = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigzzE, 'node')
            soilEffP1= self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective1, 'node')
            soilEffP2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective2, 'node')
            soilEffP3 = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective3, 'node')  
            
            soilPExcess = self.g_o.getresults(phase, self.g_o.Soil.PExcess, 'node')
            soilPActive = self.g_o.getresults(phase, self.g_o.Soil.PActive, 'node')
            soilPSteady = self.g_o.getresults(phase, self.g_o.Soil.PSteady, 'node')
            soilPWater = self.g_o.getresults(phase, self.g_o.Soil.PWater, 'node')
            
            soilSuction = self.g_o.getresults(phase, self.g_o.Soil.Suction, 'node')
            soilEffSuction = self.g_o.getresults(phase, self.g_o.Soil.EffSuction, 'node')
            
            for x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(
                soilX, soilY, soilMat, soilEl, soilUx, soilUy, soilUt, soilPUx, soilPUy, soilPUt, soilEffSxx, soilEffSyy, soilEffSzz, soilEffP1, soilEffP2, soilEffP3, soilPExcess, soilPActive, soilPSteady, soilPWater, soilSuction, soilEffSuction):
                
                if self.inRange (x_val = x, 
                                 y_val = y) == True:
                    
                    print(phase.Name.value, phase.Identification.value, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu)
          
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
           
                    locX.append(x)
                    locY.append(y)
                    
                    Uxx.append(ux)
                    Uyy.append(uy)
                    Utot.append(ut)
                    
                    PUxx.append(pux)
                    PUyy.append(puy)
                    PUtot.append(put)
                    
                    MaterialID.append(mat)
                    ElementID.append(el)
                    
                    EffSxx.append(esx)
                    EffSyy.append(esy)
                    EffSzz.append(esz)
                    
                    EffP1.append (ep1)
                    EffP2.append (ep2)
                    EffP3.append (ep3)
                    
                    PExcess.append (pe)
                    PActive.append (pa)
                    PSteady.append (ps)
                    PWater.append (pw)
        
                    Suct.append (su)
                    EffSuct.append (esu)
        columns = 'Phase,PhaseIdent,locX(m),locY(m),MaterialID,ElementID,Ux(m),Uy(m),Ut(m),PUx(m),PUy(m),PUt(m),SigxxEff(kPa),SigyyEff(kPa),SigzzEff(kPa),SigP1Eff(kPa),SigyP2Eff(kPa),SigP3Eff(kPa),PExcess(kPa),PActive(kPa),PSteady(kPa),Pwater(kPa),Suct(kPa),EffSuct(kPa)'
        formats =  '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'       
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident,  x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu )
                for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(pPhaseName, pPhaseIdent, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct, EffSuct)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident,  x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu )
                for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(pPhaseName, pPhaseIdent, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct, EffSuct)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(pPhaseName, pPhaseIdent, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct, EffSuct):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(esx)
                row.append(esy)
                row.append(esz)
                row.append(ep1)
                row.append(ep2)
                row.append(ep3)
                row.append(pe)
                row.append(pa)
                row.append(ps)
                row.append(pw)
                row.append(su)
                row.append(esu)
                
                self.insertValues(row)
                
        print('getSoilResultsByRanges Done')
         
    def getSoilResultsByPoints(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints'
        
        locName = []
        locY = []
        locX = []
        
        MaterialID = []
        ElementID =[]
        
        Uyy = []
        Uxx = []
        Utot = []
            
        PUyy = []
        PUxx = []
        PUtot = []
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []        
        
        PExcess = []
        PActive = []
        PSteady = []
        PWater = []
        
        Suct = []
        EffSuct = []
        
        pPhaseName = []
        pPhaseIdent = []
               
        if filePoints:
            fpoint = open(filePoints, "r")

            while True:
                in_line = fpoint.readline()
                if in_line == "":
                    break
                print(in_line)
                [name, nx, ny] = in_line.split(',')
                self.NodeList.append(self.PointXY(name, nx, ny))

            fpoint.close()

       

        for phase in self.phaseOrder:
            print('Getting soil results ' + phase.Identification.value)
            

                       
            for pt in self.NodeList:

                try:
                    mat = self.g_o.getsingleresult(phase, self.g_o.Soil.MaterialID, (pt.x, pt.y))
                    el = self.g_o.getsingleresult(phase, self.g_o.Soil.ElementID, (pt.x, pt.y))
                    ux = self.g_o.getsingleresult(phase, self.g_o.Soil.Ux, (pt.x, pt.y))
                    uy = self.g_o.getsingleresult(phase, self.g_o.Soil.Uy, (pt.x, pt.y))
                    ut = self.g_o.getsingleresult(phase, self.g_o.Soil.Utot, (pt.x, pt.y))
                    pux = self.g_o.getsingleresult(phase, self.g_o.Soil.PUx, (pt.x, pt.y))
                    puy = self.g_o.getsingleresult(phase, self.g_o.Soil.PUy, (pt.x, pt.y))
                    put = self.g_o.getsingleresult(phase, self.g_o.Soil.PUtot, (pt.x, pt.y))
                    esx = self.g_o.getsingleresult(phase, self.g_o.Soil.SigxxE, (pt.x, pt.y))
                    esy = self.g_o.getsingleresult(phase, self.g_o.Soil.SigyyE, (pt.x, pt.y))
                    esz = self.g_o.getsingleresult(phase, self.g_o.Soil.SigzzE, (pt.x, pt.y))
                    ep1 = self.g_o.getsingleresult(phase, self.g_o.Soil.SigmaEffective1, (pt.x, pt.y))
                    ep2 = self.g_o.getsingleresult(phase, self.g_o.Soil.SigmaEffective2, (pt.x, pt.y))
                    ep3 = self.g_o.getsingleresult(phase, self.g_o.Soil.SigmaEffective3, (pt.x, pt.y))  
                    pe = self.g_o.getsingleresult(phase, self.g_o.Soil.PExcess, (pt.x, pt.y))
                    pa = self.g_o.getsingleresult(phase, self.g_o.Soil.PActive, (pt.x, pt.y))
                    ps = self.g_o.getsingleresult(phase, self.g_o.Soil.PSteady, (pt.x, pt.y))
                    pw = self.g_o.getsingleresult(phase, self.g_o.Soil.PWater, (pt.x, pt.y))
                    su = self.g_o.getsingleresult(phase, self.g_o.Soil.Suction, (pt.x, pt.y))
                    
                    # print (pt.name, pt.x, pt.y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su) 
                    
                    if ux != 'not found':
                    
                        pPhaseName.append(phase.Name.value)
                        pPhaseIdent.append(phase.Identification.value)
                    
                        locName.append(pt.name)
                        locY.append(pt.y)
                        locX.append(pt.x)
                        
                        MaterialID.append(int(float(mat) + .1))
                        ElementID.append(int(float(el) + .1))
                        
                        Uyy.append(uy)
                        Uxx.append(ux)
                        Utot.append(ut)
                        
                        PUyy.append(puy)
                        PUxx.append(pux)
                        PUtot.append(put)
                        
                        EffSxx.append (esx)
                        EffSyy.append (esy)
                        EffSzz.append (esz)
                           
                        EffP1.append (ep1)
                        EffP2.append (ep2)
                        EffP3.append (ep3)
                            
                        PExcess.append (pe)
                        PActive.append (pa)
                        PSteady.append (ps)
                        PWater.append (pw)
                        Suct.append (su)
                     
                except:
                    print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
                    print (pt.name, pt.x, pt.y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
        columns = 'Phase,PhaseIdent,locName,locX(m),locY(m),MaterialID,ElementID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),SigxxEff(kPa),SigyyEff(kPa),SigzzEff(kPa),SigP1Eff(kPa),SigyP2Eff(kPa),SigP3Eff(kPa),PExcess(kPa),PActive(kPa),PSteady(kPa),Pwater(kPa),Suct(kPa)'  
        formats = '{},{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut != None and tableOut == None):
            try :
                print('Outputting to file ', fileOut, '....')
                columns += '\n'
                formats += '\n'
                with open(fileOut, "w") as file:
                    file.writelines([columns])
                    file.writelines([formats.format(pname, pident, locname, float(x), float(y), mat, el, float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(esx), float(esy), float(esz), float(ep1), float(ep2), float(ep3), float(pe), float(pa), float(ps), float(pw), float(su))
                                     for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)])
            except:
                print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
               #~ print (pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
                #~ print (pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(esx)
                row.append(esy)
                row.append(esz)
                row.append(ep1)
                row.append(ep2)
                row.append(ep3)
                row.append(pe)
                row.append(pa)
                row.append(ps)
                row.append(pw)
                row.append(su)
                
                self.insertValues(row)
                
        print('getSoilResultsByPoint Done')
            
    
    def getPlateResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResults'
        
        # init data for lists
        pPhaseName = []
        pPhaseIdent = []
           
        pY = []
        pX = []
        
        pMat = []
        pEl = []
        
        pUx = []
        pUy = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUt = []

        pU1 = []
        pU2 = []

        pM2D = []
        pQ2D = []
        pNx2D = []
        pNz2D = []



        for phase in self.phaseOrder:
            print('Getting Plate results ' + phase.Identification.value)
            
            try: 
                plateX = self.g_o.getresults(phase, self.g_o.Plate.X, 'node')
                plateY = self.g_o.getresults(phase, self.g_o.Plate.Y, 'node')
                
                plateMat = self.g_o.getresults(phase, self.g_o.Plate.MaterialID, 'node')
                plateEl = self.g_o.getresults(phase, self.g_o.Plate.ElementID, 'node')
                
                plateUx = self.g_o.getresults(phase, self.g_o.Plate.Ux, 'node')
                plateUy = self.g_o.getresults(phase, self.g_o.Plate.Uy, 'node')
                plateUt = self.g_o.getresults(phase, self.g_o.Plate.Utot, 'node')

                platePUx = self.g_o.getresults(phase, self.g_o.Plate.PUx, 'node')
                platePUy = self.g_o.getresults(phase, self.g_o.Plate.PUy, 'node')
                platePUt = self.g_o.getresults(phase, self.g_o.Plate.PUtot, 'node')

                plateU1 = self.g_o.getresults(phase, self.g_o.Plate.U1, 'node')
                plateU2 = self.g_o.getresults(phase, self.g_o.Plate.U2, 'node')

                plateM2D = self.g_o.getresults(phase, self.g_o.Plate.M2D, 'node')
                plateQ2D = self.g_o.getresults(phase, self.g_o.Plate.Q2D, 'node')
                plateNx2D = self.g_o.getresults(phase, self.g_o.Plate.Nx2D, 'node')
                plateNz2D = self.g_o.getresults(phase, self.g_o.Plate.Nz2D, 'node')
                
                print('...read Plate results ' + phase.Identification.value)
                
                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(
                        plateX, plateY, plateMat, plateEl, plateUx, plateUy, plateUt, platePUx, platePUy, platePUt, plateU1, plateU2, plateM2D, plateQ2D, plateNx2D, plateNz2D):
                    # add filters in here if necessary
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
                    pX.append(x)
                    pY.append(y)
                    pMat.append(mat)
                    pEl.append(el)
                    pUx.append(ux)
                    pUy.append(uy)
                    pUt.append(ut)
                    pPUx.append(pux)
                    pPUy.append(puy)
                    pPUt.append(put)
                    pU1.append(u1)
                    pU2.append(u2)
                    pM2D.append(m2d)
                    pQ2D.append(q2d)
                    pNx2D.append(nx2d)
                    pNz2D.append(nz2d)
                    
            except Exception as e:
                print ('...exception reading Plate results ' + phase.Identification.value + str(e))
                self.logger.error('...exception reading Plate results  '+ str(e))
                
        columns ='Phase,PhaseIdent,X(m),Y(m),MaterialID,ElementID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),M2D(kNm/m),Q2D(kN/m),Nx2D(kN/m),Nz2D(kN/m)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines(columns)
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pEl, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pEl, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(m2d)
                row.append(q2d)
                row.append(nx2d)
                row.append(nz2d)
                
                self.insertValues(row)
                
        print('getPlateResults Done')
    
    def getEmbeddedBeamResults (self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):
        return self.getEmbeddedBeamRowResults(fileOut=fileOut,
                                  tableOut=tableOut,
                                  sphaseOrder=sphaseOrder,
                                  sphaseStart=sphaseStart,
                                  sphaseEnd=sphaseEnd)
     
    def getEmbeddedBeamRowResults(self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getEmbeddedBeamRowResults'
        
        # init data for lists
        ePhaseName = []
        ePhaseIdent = []
           
        eY = []
        eX = []
        
        eMat = []
        eEl = []
        
        eUx = []
        eUy = []
        eUt = []

        ePUx = []
        ePUy = []
        ePUt = []

        eU1 = []
        eU2 = []

        eM2D = []
        eQ2D = []
        eNx2D = []
        eNz2D = []

        eTskin = []
        eTlat= []

        for phase in self.phaseOrder:
            #echo ResultTypes.EmbeddedBeamRow
            print ('Getting EmbeddedBeamRow results ' + phase.Identification.value)
            try:
                embeamX = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.X, 'node')
                embeamY = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Y, 'node')
                
                embeamMat = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.MaterialID, 'node')
                embeamEl = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.ElementID, 'node')
                
                embeamUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Ux, 'node')
                embeamUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Uy, 'node')
                embeamUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Utot, 'node')
                
                embeamPUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.PUx, 'node')
                embeamPUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.PUy, 'node')
                embeamPUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.PUtot, 'node')
                 
                embeamU1 = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.U1, 'node')
                embeamU2 = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.U2, 'node')

                embeamM2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.M2D, 'node')
                embeamQ2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Q2D, 'node')
                embeamNx2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Nx2D, 'node')
                embeamNz2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Nz2D, 'node')

                embeamTskin = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Tskin, 'node')
                embeamTlat= self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Tlat, 'node')
                     
                print ('...read EmbeddedBeamRow results ' + phase.Identification.value)
                
                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(
                        embeamX, embeamY, embeamMat, embeamEl, embeamUx, embeamUy, embeamUt, embeamPUx, embeamPUy, embeamPUt, embeamU1, embeamU2, embeamM2D, embeamQ2D, embeamNx2D, embeamNz2D, embeamTskin, embeamTlat):
                    # add filters in here if necessary
                    
                    ePhaseName.append(phase.Name.value)
                    ePhaseIdent.append(phase.Identification.value)
                    eX.append(x)
                    eY.append(y)
                    eMat.append(mat)
                    eEl.append(el)
                    eUx.append(ux)
                    eUy.append(uy)
                    eUt.append(ut)
                    ePUx.append(pux)
                    ePUy.append(puy)
                    ePUt.append(put)
                    eU1.append(u1)
                    eU2.append(u2)
                    eM2D.append(m2d)
                    eQ2D.append(q2d)
                    eNx2D.append(nx2d)
                    eNz2D.append(nz2d)
                    eTskin.append(tskin)
                    eTlat.append(tlat)
            except:
                print ('...exception reading EmbeddedBeamRow '  + phase.Identification.value)
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),M2D(kNm/m),Q2D(kN/m),Nx2D(kN/m),Nz2D(kN/m),Tskin(kN/m),Tlat(kN/m)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(ename, eident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat)
                                 for ename, eident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eEl, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for ename, eident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eEl, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat):
                row = []
                row.append(ename)
                row.append(eident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(m2d)
                row.append(q2d)
                row.append(nx2d)
                row.append(nz2d)
                row.append(tskin)
                row.append(tlat)
                
                self.insertValues(row)
                
        print('getEmbeddedBeamRowResults Done')
    
    
    def getNodeToNodeAnchorResults(self,
                                   fileOut=None,
                                   tableOut=None,
                                   sphaseOrder=None,
                                   sphaseStart=None,
                                   sphaseEnd=None,
                                   ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getNodeToNodeAnchorResults'
            
        # init data for lists
        aPhaseName = []
        aPhaseIdent = []
        
        aY = []
        aX = []
        
        aMat = []
        aEl = []
        
        aUx = []
        aUy = []
        
        aPUx = []
        aPUy = []
        aPUt = []
        aUt = []
        aU1 = []
        aU2 = []
        
        aForce2D = []

        for phase in self.phaseOrder:

            print('Getting NodeToNodeAnchor results for Phase ', phase.Name.value, phase.Identification.value)
            try:
                anchorX = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.X, 'node')
                anchorY = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Y, 'node')
                
                anchorMat = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.MaterialID, 'node')
                anchorEl = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.ElementID, 'node')
                
                anchorUx = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Ux, 'node')
                anchorUy = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Uy, 'node')
                anchorUt = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Utot, 'node')

                anchorPUx = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUx, 'node')
                anchorPUy = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUy, 'node')
                anchorPUt = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUtot, 'node')

                anchorU1 = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.U1, 'node')
                anchorU2 = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.U2, 'node')

                anchorForce2D = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.AnchorForce2D, 'node')

                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2D in zip(
                        anchorX, anchorY, anchorMat, anchorEl, anchorUx, anchorUy, anchorUt, anchorPUx, anchorPUy, anchorPUt, anchorU1, anchorU2, anchorForce2D):
                    # add filters in here if necessary
                    aPhaseName.append(phase.Name.value)
                    aPhaseIdent.append(phase.Identification.value)
                    aX.append(x)
                    aY.append(y)
                    aMat.append(mat)
                    aEl.append(el)
                    aUx.append(ux)
                    aUy.append(uy)
                    aUt.append(ut)
                    aPUx.append(pux)
                    aPUy.append(puy)
                    aPUt.append(put)
                    aU1.append(u1)
                    aU2.append(u2)
                    aForce2D.append(f2D)
            except:
                 print ('Exception reading  NodeToNodeAnchor in phase' + phase.Name.value, phase.Identification.value)
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),U1(m),U2(m),N(kN)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(f2d)
                
                self.insertValues(row)
                
        print('getNodeToNodeAnchorResults Done')
   
    def getFixedEndAnchorResults(self,
                                 fileOut=None,
                                 tableOut=None,
                                 sphaseOrder=None,
                                 sphaseStart=None,
                                 sphaseEnd=None
                                 ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getFixedEndAnchorResults'
        
        # init data for lists
        aPhaseName = []
        aPhaseIdent = []

        aY = []
        aX = []
        
        aMat = []
        aEl = []
        
        aUx = []
        aUy = []
        aPUx = []
        aPUy = []
        aPUt = []
        aUt = []
        aU1 = []
        aU2 = []
        
        aForce2D = []

        for phase in self.phaseOrder:

            print('Getting FixedEndAnchor results for ', phase.Name.value)
            try:
                anchorX = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.X, 'node')
                anchorY = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Y, 'node')
                
                anchorMat = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.MaterialID, 'node')
                anchorEl = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.ElementID, 'node')
                
                anchorUx = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Ux, 'node')
                anchorUy = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Uy, 'node')
                anchorUt = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Utot, 'node')

                anchorPUx = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUx, 'node')
                anchorPUy = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUy, 'node')
                anchorPUt = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUtot, 'node')

                anchorU1 = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.U1, 'node')
                anchorU2 = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.U2, 'node')

                anchorForce2D = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.AnchorForce2D, 'node')
                
                print('Retrieved FixedEndAnchor results for ', phase.Name.value)
          
                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2D in zip(
                        anchorX, anchorY, anchorMat, anchorEl, anchorUx, anchorUy, anchorUt, anchorPUx, anchorPUy, anchorPUt, anchorU1, anchorU2, anchorForce2D):
                    # add filters in here if necessary
                    aPhaseName.append(phase.Name.value)
                    aPhaseIdent.append(phase.Identification.value)
                    aX.append(x)
                    aY.append(y)
                    aMat.append(mat)
                    aEl.append(el)
                    aUx.append(ux)
                    aUy.append(uy)
                    aUt.append(ut)
                    aPUx.append(pux)
                    aPUy.append(puy)
                    aPUt.append(put)
                    aU1.append(u1)
                    aU2.append(u2)
                    aForce2D.append(f2D)
            except:
                print ('Exception reading  FixedEndAnchor in phase' + phase.Name.value)
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),U1(m),U2(m),N(kN)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D):
                 row = []
                 row.append(pname)
                 row.append(pident)
                 row.append(x)
                 row.append(y)
                 row.append(mat)
                 row.append(el)
                 row.append(ux)
                 row.append(uy)
                 row.append(ut)
                 row.append(pux)
                 row.append(puy)
                 row.append(put)
                 row.append(u1)
                 row.append(u2)
                 row.append(f2d)
                 
                 self.insertValues(row)
                 
        print('getFixedEndAnchorResults Done')
    def getInterfaceResults2016(self,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
        self.setPhaseOrder(sphaseOrder,
           sphaseStart,
           sphaseEnd)
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResults'
            
        # init data for lists
        iPhaseName = []
        iPhaseIdent = []

        iY = []
        iX = []
        iMat = []
          
        iUx = []
        iUy = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUt = []

        iU1 = []
        iU2 = []

        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            try:
                interX = self.g_o.getresults(phase, self.g_o.Interface.X, 'node')
                interY = self.g_o.getresults(phase, self.g_o.Interface.Y, 'node')
              
                interMat = self.g_o.getresults(phase, self.g_o.Interface.MaterialID, 'node')
              
                interUx = self.g_o.getresults(phase, self.g_o.Interface.Ux, 'node')
                interUy = self.g_o.getresults(phase, self.g_o.Interface.Uy, 'node')
                interUt = self.g_o.getresults(phase, self.g_o.Interface.Utot, 'node')

                interPUx = self.g_o.getresults(phase, self.g_o.Interface.PUx, 'node')
                interPUy = self.g_o.getresults(phase, self.g_o.Interface.PUy, 'node')
                interPUt = self.g_o.getresults(phase, self.g_o.Interface.PUtot, 'node')

                interU1 = self.g_o.getresults(phase, self.g_o.Interface.U1, 'node')
                interU2 = self.g_o.getresults(phase, self.g_o.Interface.U2, 'node')

                interEffNormalStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceEffectiveNormalStress, 'node')
                interTotNormalStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceTotalNormalStress, 'node')
                interShearStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceShearStress, 'node')
                interRelShearStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceRelativeShearStress, 'node')

                interPExcess = self.g_o.getresults(phase, self.g_o.Interface.PExcess, 'node')
                interPActive = self.g_o.getresults(phase, self.g_o.Interface.PActive, 'node')
                interPSteady = self.g_o.getresults(phase, self.g_o.Interface.PSteady, 'node')
                interPWater = self.g_o.getresults(phase, self.g_o.Interface.PWater, 'node')
                
                interSuction = self.g_o.getresults(phase, self.g_o.Interface.Suction, 'node')
                interEffSuction = self.g_o.getresults(phase, self.g_o.Interface.EffSuction, 'node')

                for x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(
                        interX, interY, interMat,  
                        interUx, interUy, interUt, 
                        interPUx, interPUy, interPUt, 
                        interU1, interU2, 
                        interEffNormalStress, interTotNormalStress, interShearStress, interRelShearStress,
                        interPExcess, interPActive, interPSteady, interPWater, 
                        interSuction,  interEffSuction):
                    # add filters in here if necessary
                    iPhaseName.append(phase.Name.value)
                    iPhaseIdent.append(phase.Identification.value)
                    iX.append(x)
                    iY.append(y)
                    iMat.append(mat)
                    iUx.append(ux)
                    iUy.append(uy)
                    iUt.append(ut)
                    iPUx.append(pux)
                    iPUy.append(puy)
                    iPUt.append(put)
                    iU1.append(u1)
                    iU2.append(u2)
                    iEffNormalStress.append(ens)
                    iTotNormalStress.append(tns)
                    iShearStress.append(ss)
                    iRelShearStress.append(rss)
                    iPExcess.append(pe)
                    iPActive.append(pa)
                    iPSteady.append(pst)
                    iPWater.append(pw)
                    iSuction.append(su)
                    iEffSuction.append(esu)
            except:
                print ('Exception reading Interface results in phase' + phase.Name.value)
        
        columns = "Phase,PhaseIdent,X(m),Y(m),MaterialId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)"
        formats = "{},{},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}"
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                                 for pname, pident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                                 in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                                     row = []
                                     row.append(pname)
                                     row.append(pident)
                                     row.append(x)
                                     row.append(y)
                                     row.append(mat)
                                     row.append(ux)
                                     row.append(uy)
                                     row.append(ut)
                                     row.append(pux)
                                     row.append(puy)
                                     row.append(put)
                                     row.append(u1)
                                     row.append(u2)
                                     row.append(ens)
                                     row.append(tns)
                                     row.append(ss)
                                     row.append(rss)
                                     row.append(pe)
                                     row.append(pa)
                                     row.append(pst)
                                     row.append(pw)
                                     row.append(su)
                                     row.append(esu)
                                     self.insertValues(row)
            
        print('getInterfaceResults2016 Done')   
        
    def getInterfaceResults(self,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
        self.setPhaseOrder(sphaseOrder,
           sphaseStart,
           sphaseEnd)
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResults'
        
        # init data for lists
        iPhaseName = []
        iPhaseIdent = []

        iY = []
        iX = []
        iMat = []
        iEl = []
        
        iUx = []
        iUy = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUt = []

        iU1 = []
        iU2 = []

        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            try:
                interX = self.g_o.getresults(phase, self.g_o.Interface.X, 'node')
                interY = self.g_o.getresults(phase, self.g_o.Interface.Y, 'node')
              
                interMat = self.g_o.getresults(phase, self.g_o.Interface.MaterialID, 'node')
                interEl = self.g_o.getresults(phase, self.g_o.Interface.ElementID, 'node')
              
                interUx = self.g_o.getresults(phase, self.g_o.Interface.Ux, 'node')
                interUy = self.g_o.getresults(phase, self.g_o.Interface.Uy, 'node')
                interUt = self.g_o.getresults(phase, self.g_o.Interface.Utot, 'node')

                interPUx = self.g_o.getresults(phase, self.g_o.Interface.PUx, 'node')
                interPUy = self.g_o.getresults(phase, self.g_o.Interface.PUy, 'node')
                interPUt = self.g_o.getresults(phase, self.g_o.Interface.PUtot, 'node')

                interU1 = self.g_o.getresults(phase, self.g_o.Interface.U1, 'node')
                interU2 = self.g_o.getresults(phase, self.g_o.Interface.U2, 'node')

                interEffNormalStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceEffectiveNormalStress, 'node')
                interTotNormalStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceTotalNormalStress, 'node')
                interShearStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceShearStress, 'node')
                interRelShearStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceRelativeShearStress, 'node')

                interPExcess = self.g_o.getresults(phase, self.g_o.Interface.PExcess, 'node')
                interPActive = self.g_o.getresults(phase, self.g_o.Interface.PActive, 'node')
                interPSteady = self.g_o.getresults(phase, self.g_o.Interface.PSteady, 'node')
                interPWater = self.g_o.getresults(phase, self.g_o.Interface.PWater, 'node')
                
                interSuction = self.g_o.getresults(phase, self.g_o.Interface.Suction, 'node')
                interEffSuction = self.g_o.getresults(phase, self.g_o.Interface.EffSuction, 'node')

                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(
                        interX, interY, interMat, interEl, 
                        interUx, interUy, interUt, 
                        interPUx, interPUy, interPUt, 
                        interU1, interU2, 
                        interEffNormalStress, interTotNormalStress, interShearStress, interRelShearStress,
                        interPExcess, interPActive, interPSteady, interPWater, 
                        interSuction,  interEffSuction):
                    # add filters in here if necessary
                    iPhaseName.append(phase.Name.value)
                    iPhaseIdent.append(phase.Identification.value)
                    iX.append(x)
                    iY.append(y)
                    iMat.append(mat)
                    iEl.append(el)
                    iUx.append(ux)
                    iUy.append(uy)
                    iUt.append(ut)
                    iPUx.append(pux)
                    iPUy.append(puy)
                    iPUt.append(put)
                    iU1.append(u1)
                    iU2.append(u2)
                    iEffNormalStress.append(ens)
                    iTotNormalStress.append(tns)
                    iShearStress.append(ss)
                    iRelShearStress.append(rss)
                    iPExcess.append(pe)
                    iPActive.append(pa)
                    iPSteady.append(pst)
                    iPWater.append(pw)
                    iSuction.append(su)
                    iEffSuction.append(esu)
            except:
                print ('Exception reading Interface results in phase' + phase.Name.value)
        
        columns = "Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)"
        formats = "{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}"
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                                 in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iEl, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iEl, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                                     row = []
                                     row.append(pname)
                                     row.append(pident)
                                     row.append(x)
                                     row.append(y)
                                     row.append(mat)
                                     row.append(el)
                                     row.append(ux)
                                     row.append(uy)
                                     row.append(ut)
                                     row.append(pux)
                                     row.append(puy)
                                     row.append(put)
                                     row.append(u1)
                                     row.append(u2)
                                     row.append(ens)
                                     row.append(tns)
                                     row.append(ss)
                                     row.append(rss)
                                     row.append(pe)
                                     row.append(pa)
                                     row.append(pst)
                                     row.append(pw)
                                     row.append(su)
                                     row.append(esu)
                                     self.insertValues(row)
            
        print('getInterfaceResults Done')   
        
    def getAllStructuralResults(self,
                    folderOut=None,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
                        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getPlateResults.csv'
        else:
            tableOut = 'getPlateResults'                
        self.getPlateResults (fileOut=fileOut, tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getEmbeddedBeamRowResults.csv'
        else:
            tableOut = 'getEmbeddedBeamRowResults'  
        self.getEmbeddedBeamRowResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )

        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getNodeToNodeAnchorResults.csv'
        else:
            tableOut = 'getNodeToNodeAnchorResults' 
        self.getNodeToNodeAnchorResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
                       
   
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getFixedEndAnchorResults.csv'
            tableOut = None
        else:
            tableOut = 'getFixedEndAnchorResults'
        
        self.getFixedEndAnchorResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                      )

        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getInterfaceResults.csv'
        else:
            tableOut = 'getInterfaceResults'
        self.getInterfaceResults  (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                      )
    
    def getAllStructuralResults2016(self,
                    folderOut=None,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
                        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getPlateResults.csv'
        else:
            tableOut = 'getPlateResults'                
        self.getPlateResults2016 (fileOut=fileOut, tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getEmbeddedBeamRowResults.csv'
        else:
            tableOut = 'getEmbeddedBeamRowResults'  
        self.getEmbeddedBeamRowResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )

        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getNodeToNodeAnchorResults.csv'
        else:
            tableOut = 'getNodeToNodeAnchorResults' 
        self.getNodeToNodeAnchorResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
                       
   
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getFixedEndAnchorResults.csv'
            tableOut = None
        else:
            tableOut = 'getFixedEndAnchorResults'
        
        self.getFixedEndAnchorResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                      )

        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getInterfaceResults.csv'
        else:
            tableOut = 'getInterfaceResults'
        self.getInterfaceResults2016  (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                      ) 

class Plaxis3dResults (PlaxisScripting):
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis3dResults, self).__init__(server, host, port, password)
        
        if (self.s_o.is_3d == False):
            raise ValueError('This is a Plaxis3d output reader, but the output plaxis server is not Plaxis3d');
    def version (self):
        return "Plaxis3d"

    def getPhaseDetails(self):
        results = []
        allpassed = True
        
        print('getting output phase details')
        for phase in self.g_o.Phases[:]:
            results.append( "{},{},{}\n".format(phase.Name, phase.Identification, phase.Number))

        return allpassed, results
    
    def getSoilResultsByRange(self,
                              fileOut=None,
                              tableOut=None,
                              sphaseOrder=None,
                              sphaseStart=None,
                              sphaseEnd=None,
                              xMin=0.0, xMax=0.0,
                              yMin=0.0, yMax=0.0,
                              zMin=0.0, zMax=0.0,
                              Output="stress, displacement,pwp"
                              ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByRange'  
        
        PhaseName = []
        PhaseIdent = []
        
        locY = []
        locX = []
        locZ = []
        
        Uyy = []
        Uxx = []
        Uzz = []
        Utot = []
        
        PUyy = []
        PUxx = []
        PUzz = []
        PUtot = []
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []
        
        pExcess = []
        pActive = []    
        pSteady = []
        pWater = []
        
        phasenames = []

        # look into all phases, all steps
        for phase in self.phaseOrder:
        
            print('Getting soil results for Phase ', phase.Name.value)
        
            soilX = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.X, 'node')
            soilY = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Y, 'node')
            soilZ = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Z, 'node')
             
            print('Coordinates retrieved for Phase ', phase.Name.value)
            if "displacement" in Output:
                
                soilUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Ux, 'node')
                soilUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Uy, 'node')
                soilUz = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Uz, 'node')
                soilUtot = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Utot, 'node')
                
                soilPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUx, 'node')
                soilPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUy, 'node')
                soilPUz = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUz, 'node')
                soilPUtot = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUtot, 'node') 
                print('Displacments retrieved for Phase ', phase.Name.value)
            
            if "stress" in Output:
                soilEffSxx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigxxE, 'node')
                soilEffSyy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigyyE, 'node')
                soilEffSzz = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigzzE, 'node')
                
                soilEffP1= self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective1, 'node')
                soilEffP2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective2, 'node')
                soilEffP3 = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective3, 'node')  
                print('Stresses retrieved for Phase ', phase.Name.value)
            
            if "pwp" in Output:
                soilPExcess = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PExcess, 'node')
                soilPActive = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PActive, 'node')
                soilPSteady = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PSteady, 'node')
                soilPWater = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PWater, 'node')
                print('PWP retrieved for Phase ', phase.Name.value)
            
            print('Preparing to cycle through results for nodes within range...x(', xMin, xMax, ') y(', yMin, yMax,') z (', zMin, zMax ,')')
            
            if "displacement" in Output and "stress" in Output and "pwp" in Output: 
                for x, y, z, ux, uy, uz, utot, pux, puy, puz, putot, esxx, esyy, eszz, ep1, ep2, ep3, pex, pact, pst, pw in zip(
                        soilX, soilY, soilZ, soilUx, soilUy, soilUz, soilUtot, soilPUx, soilPUy, soilPUz, soilPUtot, soilEffSxx, soilEffSyy, soilEffSzz, soilEffP1, soilEffP2, soilEffP3,soilPExcess, soilPActive, soilPSteady, soilPWater):
                
                    if xMin < x < xMax:
                        if yMin < y < yMax:
                            if zMin < z < zMax:
                                print('Adding Results for',x,y,z)
                  
                                PhaseName.append(phase.Name.value)
                                PhaseIdent.append(phase.Identification.value)
                                
                                locX.append(x)
                                locY.append(y)
                                locZ.append(z)
                                                                 
                                Uxx.append(ux)
                                Uyy.append(uy)
                                Uzz.append(uz)
                                Utot.append(utot)
                                 
                                PUxx.append(pux)
                                PUyy.append(puy)
                                PUzz.append(puz)
                                PUtot.append(putot)

                                EffSxx.append(esxx)
                                EffSyy.append(esyy)
                                EffSzz.append(eszz)
                             
                                EffP1.append(esxx)
                                EffP2.append(esyy)
                                EffP3.append(eszz)
                                

                                pExcess.append(pex)
                                pActive.append(pact) 
                                pSteady.append(pst)
                                pWater.append(pw)
                columns = 'Phase, PhaseIdent,X(m),Y(m),Z(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUtot(m),SigxxE(kPa),SigyyE(kPa),SigzzE(kPa),SigEff1(kPa),SigEff2(kPa),SigEff3(kPa),pExcess(kPa),pActive(kPa),pSteady(kPa),pWater(kPa)'
                formats =  '{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
                
                if (fileOut == None and tableOut == None):
                    print('Outputting to string....')
                    columns += '\n'
                    formats += '\n'
                    rows = ''.join([formats.format(pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, put, esxx, esyy, eszz, ep1, ep2, ep3, pex, pact, pst, pw)
                            for pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, put, esxx, esyy, eszz, ep1, ep2, ep3, pex, pact, pst, pw in zip(PhaseName, PhaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, pExcess, pActive, pSteady, pWater)])
                    return columns + rows

                if (fileOut != None and tableOut == None):
                    print('Outputting to file ', fileOut, '....')  
                    columns += '\n'
                    formats += '\n'
                    with open(fileOut, "w") as file:
                        file.writelines([columns])
                        file.writelines([formats.format(pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, put, esxx, esyy, eszz, ep1, ep2, ep3, pex, pact, pst, pw)
                            for pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, put, esxx, esyy, eszz, ep1, ep2, ep3, pex, pact, pst, pw in zip(PhaseName, PhaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, pExcess, pActive, pSteady, pWater)])
                
                if (fileOut != None and tableOut != None):
                    print('Outputting to database ', fileOut, '....')

                    self.getConnected (fileOut)
                    self.createTable(tableOut, columns, formats)
                    for pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, put, esxx, esyy, eszz, ep1, ep2, ep3, pex, pact, pst, pw in zip(PhaseName, PhaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, pExcess, pActive, pSteady, pWater):
                        row = []
                        row.append(pName)
                        row.append(pIdent)
                        row.append(x)
                        row.append(y)
                        row.append(z)
                        row.append(ux)
                        row.append(uy)
                        row.append(uz)
                        row.append(utot)
                        row.append(pux)
                        row.append(puy)
                        row.append(puz)
                        row.append(put)
                        row.append(esxx)
                        row.append(esyy)
                        row.append(eszz)
                        row.append(ep1)
                        row.append(ep2)
                        row.append(ep3)
                        row.append(pex)
                        row.append(pact)
                        row.append(pst)
                        row.append(pw)
                        self.insertValues(row)
                    
            if "displacement" in Output and not "stress" in Output and not "pwp" in Output: 
                for x, y, z, ux, uy, uz, utot, pux, puy, puz, dutot in zip(
                        soilX, soilY, soilZ, soilUx, soilUy, soilUz, soilUtot, soilPUx, soilPUy, soilPUz, soilPUtot):
                    print (x, y, z)
                    if xMin < x < xMax:
                        if yMin < y < yMax:
                            if zMin < z < zMax:
                                print('Adding Results for',x,y,z)
                  
                                PhaseName.append(phase.Name.value)
                                PhaseIdent.append(phase.Identification.value)
                                
                                locX.append(x)
                                locY.append(y)
                                locZ.append(z)
                                
                                Uxx.append(ux)
                                Uyy.append(uy)
                                Uzz.append(uz)
                                Utot.append(utot)
                                 
                                PUxx.append(pux)
                                PUyy.append(puy)
                                PUzz.append(puz)
                                PUtot.append(putot)  
                columns='Phase, PhaseIdent,X(m),Y(m),Z(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m)'
                formats='{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'                
                if (fileOut != None and tableOut == None):
                    print('Outputting to file ', fileOut, '....')
                    columns += '\n'
                    formats += '\n'
                    with open(fileOut, "w") as file:
                        file.writelines([columns])
                        file.writelines([formats.format(pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, putot)
                            for x, y, z, ux, uy, uz, utot, pux, puy, puz, dutot in zip(PhaseName, PhaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot)])
                if (fileOut != None and tableOut != None):
                    print('Outputting to database ', fileOut, '....')
                    self.getConnected (fileOut)
                    self.createTable(tableOut, columns, formats)
                    for x, y, z, ux, uy, uz, utot, pux, puy, puz, dutot in zip(PhaseName, PhaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot):
                        row=[]
                        row.append(x)
                        row.append(y)
                        row.append(z)
                        row.append(ux)
                        row.append(uy)
                        row.append(uz)
                        row.append(utot)
                        row.append(pux)
                        row.append(puy)
                        row.append(puz)
                        row.append(dutot)
                        self.insertValues(row)
                        
    def getSoilResultsByPoints(self,
                              fileOut=None,
                              tableOut=None,
                              sphaseOrder=None,
                              sphaseStart=None,
                              sphaseEnd=None,
                              Output="stress, displacement,pwp",
                              xMin=0.0, xMax=0.0,
                              yMin=0.0, yMax=0.0,
                              zMin=0.0, zMax=0.0,
                              ):
                              
        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByRange2'  
        
        
        
        phaseName = []
        phaseIdent = []
        
        locY = []
        locX = []
        locZ = []
           
        Uyy = []
        Uxx = []
        Uzz = []
        Utot = []
        
        PUyy = []
        PUxx = []
        PUzz = []
        PUtot = []
        
        self.setNodeList (xMin, xMax,
                          yMin, yMax,
                          zMin, zMax)
       
        for phase in self.phaseOrder:
            
            print('retrieving results for ', phase.Name.value)  

            for pt in self.NodeList:
                ux = self.g_o.getsingleresult(phase, self.g_o.Soil.Ux, (pt.x, pt.y, pt.z))
                uy = self.g_o.getsingleresult(phase, self.g_o.Soil.Uy, (pt.x, pt.y, pt.z))
                uz = self.g_o.getsingleresult(phase, self.g_o.Soil.Uz, (pt.x, pt.y, pt.z))
                utot = self.g_o.getsingleresult(phase, self.g_o.Soil.Utot, (pt.x, pt.y, pt.z))
                pux = self.g_o.getsingleresult(phase, self.g_o.Soil.PUx, (pt.x, pt.y, pt.z))
                puy = self.g_o.getsingleresult(phase, self.g_o.Soil.PUy, (pt.x, pt.y, pt.z))
                puz = self.g_o.getsingleresult(phase, self.g_o.Soil.PUz, (pt.x, pt.y, pt.z))
                putot = self.g_o.getsingleresult(phase, self.g_o.Soil.PUtot, (pt.x, pt.y, pt.z)) 
                
                # sxx = self.g_o.getsingleresult(phase, self.g_o.Soil.SigxxE, (pt.x, pt.y, pt.z))
                # syy = self.g_o.getsingleresult(phase, self.g_o.Soil.SigyyE, (pt.x, pt.y, pt.z))
                # szz = self.g_o.getsingleresult(phase, self.g_o.Soil.SigzzE, (pt.x, pt.y, pt.z))
                # xpwp = self.g_o.getsingleresult(phase, self.g_o.Soil.PExcess, (pt.x, pt.y, pt.z))
                
                print('results for ', phase.Name.value, pt.x, pt.y, pt.z ,' retrieved')
                
                phaseName.append(phase.Name.value)
                phaseIdent.append(phase.Identification.value)
              
                locX.append (pt.x)
                locY.append (pt.y)
                locZ.append (pt.z)
                               
                Uxx.append (ux)
                Uyy.append (uy)
                Uzz.append (uz)
                Utot.append (utot)
                
                PUxx.append (pux)
                PUyy.append (puy)
                PUzz.append (puy)
                PUtot.append (putot)
         
        columns='Phase, PhaseIdent,X(m),Y(m),Z(m),MaterialId,ElementId,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m)'
        formats='{},{},{:2f},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'                
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, putot)
                for pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, dutot in zip(phaseName, phaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pName, pIdent, x, y, z, ux, uy, uz, utot, pux, puy, puz, dutot in zip(phaseName, phaseIdent, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot):
                row=[]
                row.append(pName)
                row.append(pIdent)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(utot)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(dutot)
                self.insertValues(row)                
                  
    def getSoilResultsByPoints(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):
        self.getSoilResultsByPoints_Displacements(
                               filePoints=filePoints,
                               fileOut=fileOut,
                               tableOut=tableOut,
                               sphaseOrder=sphaseOrder,
                               sphaseStart=sphaseStart,
                               sphaseEnd=sphaseEnd,
                               )                           
    def getSoilResultsByPoints_Displacements(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        
        if not filePoints is None:
            self.loadXYZNodeList(filePoints)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints_Displacements'  
            
        phaseName = []
        phaseIdent = []
        
        locName = []
        locY = []
        locX = []
        locZ = []
       
        Uyy = []
        Uxx = []
        Uzz = []
        Utot = []
        
        PUyy = []
        PUxx = []
        PUzz = []
        PUtot = []
        
        Epsyy = []
        Epsxx = []
        Epszz = []

            
        for phase in self.phaseOrder:
            print(phase.Name.value)
    
            for pt in self.NodeList:
            
                ux = self.g_o.getsingleresult(phase, self.g_o.Soil.Ux, (pt.x, pt.y, pt.z))
                uy = self.g_o.getsingleresult(phase, self.g_o.Soil.Uy, (pt.x, pt.y, pt.z))
                uz = self.g_o.getsingleresult(phase, self.g_o.Soil.Uz, (pt.x, pt.y, pt.z))
                utot = self.g_o.getsingleresult(phase, self.g_o.Soil.Utot, (pt.x, pt.y, pt.z))
                 
                pux = self.g_o.getsingleresult(phase, self.g_o.Soil.PUx, (pt.x, pt.y, pt.z))
                puy = self.g_o.getsingleresult(phase, self.g_o.Soil.PUy, (pt.x, pt.y, pt.z))
                puz = self.g_o.getsingleresult(phase, self.g_o.Soil.PUz, (pt.x, pt.y, pt.z))
                putot = self.g_o.getsingleresult(phase, self.g_o.Soil.PUtot, (pt.x, pt.y, pt.z)) 
                
                ex = self.g_o.getsingleresult(phase, self.g_o.Soil.Epsxx, (pt.x, pt.y, pt.z))
                ey = self.g_o.getsingleresult(phase, self.g_o.Soil.Epsyy, (pt.x, pt.y, pt.z))
                ez = self.g_o.getsingleresult(phase, self.g_o.Soil.Epszz, (pt.x, pt.y, pt.z))
                
                if ux != 'not found':
                    print('results for ', phase.Name.value, pt.x, pt.y, pt.z ,' retrieved')
                
                    phaseName.append(phase.Name.value)
                    phaseIdent.append(phase.Identification.value)
                
                    locName.append (pt.name)
                    locX.append (pt.x)
                    locY.append (pt.y)
                    locZ.append (pt.z)
                                     
                    Uxx.append (ux)
                    Uyy.append (uy)
                    Uzz.append (uz)
                    Utot.append (utot)
                
                    PUxx.append (pux)
                    PUyy.append (puy)
                    PUzz.append (puz)
                    PUtot.append (putot)
                
                    Epsxx.append (ex)
                    Epsyy.append (ey)
                    Epszz.append (ez)
              
                
        columns='Phase,PhaseIdent,locName,locX(m),locY(m),locZ(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUtot(m),Epsxx,Epsyy,Epszz'
        formats='{},{},{},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f}'                
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pName, pIdent,locname, float(x), float(y), float(z), float(ux), float(uy), float(uz), float(utot), float(pux), float(puy), float(puz), float(putot), float(ex), float(ey), float(ez))
                for pName, pIdent, locname, x, y, z, ux, uy, uz, utot, pux, puy, puz, putot, ex, ey, ez in zip(phaseName, phaseIdent, locName, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, Epsxx, Epsyy, Epszz)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pName, pIdent, locname, x, y, z, ux, uy, uz, utot, pux, puy, puz, putot, ex, ey, ez in zip(phaseName, phaseIdent, locName, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, Epsxx, Epsyy, Epszz):
                row = []
                row.append(pName)
                row.append(pIdent)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(utot)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(putot)
                row.append(ex)
                row.append(ey)
                row.append(ez)
                self.insertValues(row)
                
    def getSoilResultsByPoints_Stresses(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
                           
        if not filePoints is None:
            self.loadXYZNodeList(filePoints)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints_Stresses'  
        
        phaseName = []
        phaseIdent = []
        
        locName = []
        locY = []
        locX = []
        locZ = []
        
        Uyy = []
        Uxx = []
        Uzz = []
        Utot = []
        
        SigxxT = []
        SigyyT = []
        SigzzT = []
        
        Sigxy = []
        Sigyz = []
        Sigzx = []

            
        for phase in self.phaseOrder:
            print(phase.Name.value)
    
            for pt in self.NodeList:
            
                ux = self.g_o.getsingleresult(phase, self.g_o.Soil.Ux, (pt.x, pt.y, pt.z))
                uy = self.g_o.getsingleresult(phase, self.g_o.Soil.Uy, (pt.x, pt.y, pt.z))
                uz = self.g_o.getsingleresult(phase, self.g_o.Soil.Uz, (pt.x, pt.y, pt.z))
                utot = self.g_o.getsingleresult(phase, self.g_o.Soil.Utot, (pt.x, pt.y, pt.z))
             
                sig_xxt = self.g_o.getsingleresult(phase, self.g_o.Soil.SigxxT, (pt.x, pt.y, pt.z))
                sig_yyt = self.g_o.getsingleresult(phase, self.g_o.Soil.SigyyT, (pt.x, pt.y, pt.z))
                sig_zzt = self.g_o.getsingleresult(phase, self.g_o.Soil.SigzzT, (pt.x, pt.y, pt.z))
                            
                sig_xy = self.g_o.getsingleresult(phase, self.g_o.Soil.Sigxy, (pt.x, pt.y, pt.z))
                sig_yz = self.g_o.getsingleresult(phase, self.g_o.Soil.Sigyz, (pt.x, pt.y, pt.z))
                sig_zx = self.g_o.getsingleresult(phase, self.g_o.Soil.Sigzx, (pt.x, pt.y, pt.z))
                
                if ux != 'not found':
                    print('results for ', phase.Name.value, pt.x, pt.y, pt.z ,' retrieved')
                
                    phaseName.append(phase.Name.value)
                    phaseIdent.append(phase.Identification.value)
                    locName.append (pt.name)
                    
                    locX.append (pt.x)
                    locY.append (pt.y)
                    locZ.append (pt.z)
                    
                    Uxx.append (ux)
                    Uyy.append (uy)
                    Uzz.append (uz)
                    Utot.append (utot)
                
                    SigxxT.append (sig_xxt)
                    SigyyT.append (sig_yyt)
                    SigzzT.append (sig_zzt)
                
                    Sigxy.append (sig_xy)
                    Sigyz.append (sig_yz)
                    Sigzx.append (sig_zx)
              
                
        columns='Phase,PhaseIdent,locName,locX(m),locY(m),locZ(m),Ux(m),Uy(m),Uz(m),Utot(m),SxxT,SyyT,SzzT,Sxy,Syz,Szx'
        formats='{},{},{},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f}'                
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            try: 
                with open(fileOut, "w") as file:
                    file.writelines([columns])
                    file.writelines([formats.format(pName, pIdent,locname, float(x), float(y), float(z), float(ux), float(uy), float(uz), float(utot), float(sig_xxt), float(sig_yyt), float(sig_zzt), float(sig_xy), float(sig_yz), float(sig_zx))
                    for pName, pIdent, locname, x, y, z, ux, uy, uz, utot, sig_xxt, sig_yyt, sig_zzt, sig_xy, sig_yz, sig_zx in zip(phaseName, phaseIdent, locName, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, SigxxT, SigyyT, SigzzT, Sigxy, Sigyz, Sigzx)])
            except:
                print ('Exception writing fileoutput')    
        print("end")
        file.close
        
    def getPlateResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResults'  
        print('FileOut=', fileOut)

        # initialise data for lists
        pPhaseName = []
        pPhaseIdent = []
           
        pY = []
        pX = []
        pZ = []
        
        pMat = []
               
        pUx = []
        pUy = []
        pUz = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUz = []
        pPUt = []

        pU1 = []
        pU2 = []
        pU3 = []
        
        pM11 = []
        pM22 = []
        pM12 = []
        
        pQ12 = []
        pQ23 = [] 
        pQ13 = []
        
        pN1 = []
        pN2 = []



        for phase in self.phaseOrder:
            print('Getting Plate results for Phase ', phase.Name.value, phase.Identification.value)
            
            try: 
                plateX = self.g_o.getresults(phase, self.g_o.Plate.X, 'node')
                plateY = self.g_o.getresults(phase, self.g_o.Plate.Y, 'node')
                plateZ = self.g_o.getresults(phase, self.g_o.Plate.Z, 'node')
                
                plateMat = self.g_o.getresults(phase, self.g_o.Plate.MaterialID, 'node')
                #~ plateEl =  self.g_o.getresults(phase, self.g_o.Plate.ElementID, 'node')
                
                plateUx = self.g_o.getresults(phase, self.g_o.Plate.Ux, 'node')
                plateUy = self.g_o.getresults(phase, self.g_o.Plate.Uy, 'node')
                plateUz = self.g_o.getresults(phase, self.g_o.Plate.Uz, 'node')
                plateUt = self.g_o.getresults(phase, self.g_o.Plate.Utot, 'node')

                platePUx = self.g_o.getresults(phase, self.g_o.Plate.PUx, 'node')
                platePUy = self.g_o.getresults(phase, self.g_o.Plate.PUy, 'node')
                platePUz = self.g_o.getresults(phase, self.g_o.Plate.PUz, 'node')
                platePUt = self.g_o.getresults(phase, self.g_o.Plate.PUtot, 'node')

                plateU1 = self.g_o.getresults(phase, self.g_o.Plate.U1, 'node')
                plateU2 = self.g_o.getresults(phase, self.g_o.Plate.U2, 'node')
                plateU3 = self.g_o.getresults(phase, self.g_o.Plate.U3, 'node')
                
                plateN1 = self.g_o.getresults(phase, self.g_o.Plate.N11, 'node')
                plateN2 = self.g_o.getresults(phase, self.g_o.Plate.N22, 'node')                
                plateQ12 = self.g_o.getresults(phase, self.g_o.Plate.Q12, 'node')
                plateQ23 = self.g_o.getresults(phase, self.g_o.Plate.Q23, 'node')
                plateQ13 = self.g_o.getresults(phase, self.g_o.Plate.Q13, 'node')
                plateM11 = self.g_o.getresults(phase, self.g_o.Plate.M11, 'node')
                plateM22 = self.g_o.getresults(phase, self.g_o.Plate.M22, 'node')
                plateM12 = self.g_o.getresults(phase, self.g_o.Plate.M12, 'node')
                
                #~ print (plateEl)
                
                for x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(
                        plateX, plateY, plateZ, plateMat, plateUx, plateUy, plateUz, plateUt, platePUx, platePUy, platePUz, platePUt, plateU1, plateU2, plateU3, plateN1, plateN2, plateQ12, plateQ23, plateQ13, plateM11, plateM22, plateM12):
                    # add filters in here if necessary
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
                    
                    pX.append(x)
                    pY.append(y)
                    pZ.append(z)
                    pMat.append(mat)
                   
                    pUx.append(ux)
                    pUy.append(uy)
                    pUz.append(uz)
                    pUt.append(ut)
                    
                    pPUx.append(pux)
                    pPUy.append(puy)
                    pPUz.append(puz)
                    pPUt.append(put)
                   
                    pU1.append(u1)
                    pU2.append(u2)
                    pU3.append(u3)
                    
                    pN1.append(n1)
                    pN2.append(n2)
                    pQ12.append(q12)
                    pQ23.append(q23)
                    pQ13.append(q13)
                    pM11.append(m11)                    
                    pM22.append(m22)                  
                    pM12.append(m12) 
            except:
                print ('Exception reading Plate in phase' + phase.Name.value)

        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N1(kN/m),N2(kN/m),Q12(kN/m),Q23(kN/m),Q13(kN/m),M11(kNm/m),M22(kNm/m),M12(kNm/m)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12)
                                 for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12)
                                 for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            print (self.columns)
            print (self.formats)
            print (self.types)
            for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12):
                row= []
                row.append(pname) 
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n1)
                row.append(n2)
                row.append(q12)
                row.append(q23)
                row.append(q13)
                row.append(m11)
                row.append(m22)
                row.append(m12)
                self.insertValues(row)
        
        print('getPlateResults Done')
        
    def getPlateResultsByPoints(self,
                        filePoints=None,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
  
        if not filePoints is None:
            self.loadXYZNodeList(filePoints)
        
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResultsByPoints'  
        print('FileOut=', fileOut)

        # initialise data for lists
        pPhaseName = []
        pPhaseIdent = []
                
        pLocName = []
        
        pY = []
        pX = []
        pZ = []
        
        pMat = []
               
        pUx = []
        pUy = []
        pUz = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUz = []
        pPUt = []

        pU1 = []
        pU2 = []
        pU3 = []
        
        pM11 = []
        pM22 = []
        pM12 = []
        
        pQ12 = []
        pQ23 = [] 
        pQ13 = []
        
        pN1 = []
        pN2 = []



        for phase in self.phaseOrder:
            print('Getting Plate results for Phase ', phase.Name.value, phase.Identification.value)
            
            for pt in self.NodeList:
                try: 
                    
                    mat = self.g_o.getsingleresult(phase, self.g_o.Plate.MaterialID, (pt.x, pt.y, pt.z))
                                    
                    ux = self.g_o.getsingleresult(phase, self.g_o.Plate.Ux, (pt.x, pt.y, pt.z))
                    uy = self.g_o.getsingleresult(phase, self.g_o.Plate.Uy, (pt.x, pt.y, pt.z))
                    uz = self.g_o.getsingleresult(phase, self.g_o.Plate.Uz, (pt.x, pt.y, pt.z))
                    ut = self.g_o.getsingleresult(phase, self.g_o.Plate.Utot, (pt.x, pt.y, pt.z))

                    pux = self.g_o.getsingleresult(phase, self.g_o.Plate.PUx, (pt.x, pt.y, pt.z))
                    puy = self.g_o.getsingleresult(phase, self.g_o.Plate.PUy, (pt.x, pt.y, pt.z))
                    puz = self.g_o.getsingleresult(phase, self.g_o.Plate.PUz, (pt.x, pt.y, pt.z))
                    put = self.g_o.getsingleresult(phase, self.g_o.Plate.PUtot, (pt.x, pt.y, pt.z))

                    u1 = self.g_o.getsingleresult(phase, self.g_o.Plate.U1, (pt.x, pt.y, pt.z))
                    u2 = self.g_o.getsingleresult(phase, self.g_o.Plate.U2, (pt.x, pt.y, pt.z))
                    u3 = self.g_o.getsingleresult(phase, self.g_o.Plate.U3, (pt.x, pt.y, pt.z))
                    
                    n1 = self.g_o.getsingleresult(phase, self.g_o.Plate.N11, (pt.x, pt.y, pt.z))
                    n2 = self.g_o.getsingleresult(phase, self.g_o.Plate.N22, (pt.x, pt.y, pt.z))                
                    q12 = self.g_o.getsingleresult(phase, self.g_o.Plate.Q12, (pt.x, pt.y, pt.z))
                    q23 = self.g_o.getsingleresult(phase, self.g_o.Plate.Q23, (pt.x, pt.y, pt.z))
                    q13 = self.g_o.getsingleresult(phase, self.g_o.Plate.Q13, (pt.x, pt.y, pt.z))
                    m11 = self.g_o.getsingleresult(phase, self.g_o.Plate.M11, (pt.x, pt.y, pt.z))
                    m22 = self.g_o.getsingleresult(phase, self.g_o.Plate.M22, (pt.x, pt.y, pt.z))
                    m12 = self.g_o.getsingleresult(phase, self.g_o.Plate.M12, (pt.x, pt.y, pt.z))
                    
                    if ux == 'not found':
                        print('results for ', phase.Name.value, pt.name, pt.x, pt.y, pt.z ,' not found')
                    if ux != 'not found':
                        print('results for ', phase.Name.value, pt.name, pt.x, pt.y, pt.z ,' retrieved')
                        # add filters in here if necessary
                        pPhaseName.append(phase.Name.value)
                        pPhaseIdent.append(phase.Identification.value)
                        
                        pX.append(pt.x)
                        pY.append(pt.y)
                        pZ.append(pt.z)
                        
                        pMat.append(int(float(mat) + .1))
                        pLocName.append (pt.name)
                        
                        pUx.append(ux)
                        pUy.append(uy)
                        pUz.append(uz)
                        pUt.append(ut)
                        
                        pPUx.append(pux)
                        pPUy.append(puy)
                        pPUz.append(puz)
                        pPUt.append(put)
                       
                        pU1.append(u1)
                        pU2.append(u2)
                        pU3.append(u3)
                        
                        pN1.append(n1)
                        pN2.append(n2)
                        pQ12.append(q12)
                        pQ23.append(q23)
                        pQ13.append(q13)
                        pM11.append(m11)                    
                        pM22.append(m22)                  
                        pM12.append(m12)
                        
                except:
                    print ('Exception reading Plate in phase' + phase.Name.value)

        columns ='Phase,PhaseIdent,LocName, X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N1(kN/m),N2(kN/m),Q12(kN/m),Q23(kN/m),Q13(kN/m),M11(kNm/m),M22(kNm/m),M12(kNm/m)'
        formats = '{},{},{},{:2f},{:2f},{:2f},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, plocname, float(x), float(y), float(z), mat, float(ux), float(uy), float(uz), float(ut), float(pux), float(puy), float(puz), float(put), float(u1), float(u2), float(u3), float(n1), float(n2), float(q12), float(q23), float(q13), float(m11), float(m22), float(m12))
                                 for pname, pident, plocname, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pLocName, pX, pY, pZ, pMat, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, plocname, float(x), float(y), float(z), mat, float(ux), float(uy), float(uz), float(ut), float(pux), float(puy), float(puz), float(put), float(u1), float(u2), float(u3), float(n1), float(n2), float(q12), float(q23), float(q13), float(m11), float(m22), float(m12))
                                 for pname, pident, plocname, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pLocName, pX, pY, pZ, pMat, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            print (self.columns)
            print (self.formats)
            print (self.types)
            for pname, pident,locname, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pLocName, pX, pY, pZ, pMat, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12):
                row= []
                row.append(pname) 
                row.append(pident)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n1)
                row.append(n2)
                row.append(q12)
                row.append(q23)
                row.append(q13)
                row.append(m11)
                row.append(m22)
                row.append(m12)
                self.insertValues(row)
        
        print('getPlateResultsByPoints Done')       
   
    def getInterfaceResultsByPoints(self,
                        filePoints=None,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
  
        if not filePoints is None:
            self.loadXYZNodeList(filePoints)
        
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResultsByPoints'  
        
        print('FileOut=', fileOut)

        # initialize data for lists
        iPhaseName = []
        iPhaseIdent = []
        
        iLocName = []
        
        iY = []
        iX = []
        iZ = []
        
        iMat = []
               
        iUx = []
        iUy = []
        iUz = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUz = []
        iPUt = []

        iU1 = []
        iU2 = []
        iU3 = []
        
        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            
            for pt in self.NodeList:
            
                try:
                    x = self.g_o.getsingleresult(phase, self.g_o.Interface.X, (pt.x, pt.y, pt.z))
                    y = self.g_o.getsingleresult(phase, self.g_o.Interface.Y, (pt.x, pt.y, pt.z))
                    z = self.g_o.getsingleresult(phase, self.g_o.Interface.Z, (pt.x, pt.y, pt.z))
                    mat = self.g_o.getsingleresult(phase, self.g_o.Interface.MaterialID,  (pt.x, pt.y, pt.z))
                                   
                    ux = self.g_o.getsingleresult(phase, self.g_o.Interface.Ux, (pt.x, pt.y, pt.z))
                    uy = self.g_o.getsingleresult(phase, self.g_o.Interface.Uy, (pt.x, pt.y, pt.z))
                    uz = self.g_o.getsingleresult(phase, self.g_o.Interface.Uz, (pt.x, pt.y, pt.z))
                    ut = self.g_o.getsingleresult(phase, self.g_o.Interface.Utot, (pt.x, pt.y, pt.z))

                    pux = self.g_o.getsingleresult(phase, self.g_o.Interface.PUx, (pt.x, pt.y, pt.z))
                    puy = self.g_o.getsingleresult(phase, self.g_o.Interface.PUy, (pt.x, pt.y, pt.z))
                    puz = self.g_o.getsingleresult(phase, self.g_o.Interface.PUz, (pt.x, pt.y, pt.z))
                    put = self.g_o.getsingleresult(phase, self.g_o.Interface.PUtot, (pt.x, pt.y, pt.z))

                    u1 = self.g_o.getsingleresult(phase, self.g_o.Interface.U1, (pt.x, pt.y, pt.z))
                    u2 = self.g_o.getsingleresult(phase, self.g_o.Interface.U2, (pt.x, pt.y, pt.z))
                    u3 = self.g_o.getsingleresult(phase, self.g_o.Interface.U3, (pt.x, pt.y, pt.z))
                    
                    ens = self.g_o.getsingleresult(phase, self.g_o.Interface.InterfaceEffectiveNormalStress, (pt.x, pt.y, pt.z))
                    tns = self.g_o.getsingleresult(phase, self.g_o.Interface.InterfaceTotalNormalStress, (pt.x, pt.y, pt.z))
                    ss = self.g_o.getsingleresult(phase, self.g_o.Interface.InterfaceShearStress, (pt.x, pt.y, pt.z))
                    rss = self.g_o.getsingleresult(phase, self.g_o.Interface.InterfaceRelativeShearStress, (pt.x, pt.y, pt.z))

                    pe = self.g_o.getsingleresult(phase, self.g_o.Interface.PExcess, (pt.x, pt.y, pt.z))
                    pa = self.g_o.getsingleresult(phase, self.g_o.Interface.PActive, (pt.x, pt.y, pt.z))
                    pst = self.g_o.getsingleresult(phase, self.g_o.Interface.PSteady, (pt.x, pt.y, pt.z))
                    pw = self.g_o.getsingleresult(phase, self.g_o.Interface.PWater, (pt.x, pt.y, pt.z))
                    
                    su = self.g_o.getsingleresult(phase, self.g_o.Interface.Suction, (pt.x, pt.y, pt.z))
                    esu = self.g_o.getsingleresult(phase, self.g_o.Interface.EffSuction, (pt.x, pt.y, pt.z))
                    
                    if ux == 'not found':
                        print('results for ', phase.Name.value, pt.name, pt.x, pt.y, pt.z ,' not found')
                    if ux != 'not found':
                        print('results for ', phase.Name.value, pt.name, pt.x, pt.y, pt.z ,' retrieved')
                        # add filters in here if necessary
                        iPhaseName.append(phase.Name.value)
                        iPhaseIdent.append(phase.Identification.value)
                        
                        iX.append(x)
                        iY.append(y)
                        iZ.append(z)
                        
                        iMat.append(mat)
                        iLocName.append (pt.name)
                        
                        iUx.append(ux)
                        iUy.append(uy)
                        iUz.append(uz)
                        iUt.append(ut)
                        
                        iPUx.append(pux)
                        iPUy.append(puy)
                        iPUz.append(puz)
                        iPUt.append(put)
                        
                        iU1.append(u1)
                        iU2.append(u2)
                        iU3.append(u3)
                         
                        iEffNormalStress.append(ens)
                        iTotNormalStress.append(tns)
                        iShearStress.append(ss)
                        iRelShearStress.append(rss)
                        iPExcess.append(pe)
                        iPActive.append(pa)
                        iPSteady.append(pst)
                        iPWater.append(pw)
                        iSuction.append(su)
                        iEffSuction.append(esu)
                        
                except:
                    print ('Exception reading Interface results in phase' + phase.Name.value)
        
        columns ='Phase,PhaseIdent,LocName,X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)'
        formats = '{},{},{},{:2f},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, loc, float(x), float(y), float(z), float(mat), float(ux), float(uy), float(uz), float(ut), float(pux), float(puy), float(puz), float(put), float(u1), float(u2),float(u3), float(ens), float(tns), float(ss), float(rss), float(pe), float(pa), float(pst), float(pw), float(su), float(esu))
                for pname, pident, loc, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            
            #~ print(iLocName)
            #~ print(iPhaseName)
            #~ print(iPhaseIdent)
            #~ print(iX)
            #~ print(iY)
            #~ print(iZ)
            #~ print(iMat)
            
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, loc, float(x), float(y), float(z), float(mat), float(ux), float(uy), float(uz), float(ut), float(pux), float(puy), float(puz), float(put), float(u1), float(u2),float(u3), float(ens), float(tns), float(ss), float(rss), float(pe), float(pa), float(pst), float(pw), float(su), float(esu))
                for pname, pident, loc, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, loc, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(loc)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(ens)
                row.append(tns)
                row.append(ss)
                row.append(rss)
                row.append(pe)
                row.append(pa)
                row.append(pst)
                row.append(pw)
                row.append(su)
                row.append(esu)
                self.insertValues(row)
        
        print('getInterfaceResultsByPoints Done') 
        
    def getBeamResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getBeamResults'
        print('FileOut=', fileOut)

        # initialise data for lists
        bPhaseName = []
        bPhaseIdent = []
           
        bMat = []
        bY = []
        bX = []
        bZ = []
        
        bUx = []
        bUy = []
        bUz = []
        bUt = []

        bPUx = []
        bPUy = []
        bPUz = []
        bPUt = []

        bU1 = []
        bU2 = []
        bU3 = []
        
        bM2 = []
        bM3 = []
        
        bQ12 = []
        bQ13 = [] 
        
        bN = []
      

        for phase in self.phaseOrder:
            print('Getting Beam results for Phase ', phase.Name.value, phase.Identification.value)
            
            try: 
                beamMat = self.g_o.getresults(phase, self.g_o.Beam.MaterialID, 'node')     
                beamX = self.g_o.getresults(phase, self.g_o.Beam.X, 'node')
                beamY = self.g_o.getresults(phase, self.g_o.Beam.Y, 'node')
                beamZ = self.g_o.getresults(phase, self.g_o.Beam.Z, 'node')
                
                beamUx = self.g_o.getresults(phase, self.g_o.Beam.Ux, 'node')
                beamUy = self.g_o.getresults(phase, self.g_o.Beam.Uy, 'node')
                beamUz = self.g_o.getresults(phase, self.g_o.Beam.Uz, 'node')
                beamUt = self.g_o.getresults(phase, self.g_o.Beam.Utot, 'node')

                beamPUx = self.g_o.getresults(phase, self.g_o.Beam.PUx, 'node')
                beamPUy = self.g_o.getresults(phase, self.g_o.Beam.PUy, 'node')
                beamPUz = self.g_o.getresults(phase, self.g_o.Beam.PUz, 'node')
                beamPUt = self.g_o.getresults(phase, self.g_o.Beam.PUtot, 'node')

                beamU1 = self.g_o.getresults(phase, self.g_o.Beam.U1, 'node')
                beamU2 = self.g_o.getresults(phase, self.g_o.Beam.U2, 'node')
                beamU3 = self.g_o.getresults(phase, self.g_o.Beam.U3, 'node')
                
                beamN = self.g_o.getresults(phase, self.g_o.Beam.N, 'node')
                beamQ12 = self.g_o.getresults(phase, self.g_o.Beam.Q12, 'node')
                beamQ13 = self.g_o.getresults(phase, self.g_o.Beam.Q13, 'node')
                beamM2 = self.g_o.getresults(phase, self.g_o.Beam.M2, 'node')
                beamM3 = self.g_o.getresults(phase, self.g_o.Beam.M3, 'node')
                     
                for mat, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(
                        beamMat, beamX, beamY, beamZ, beamUx, beamUy, beamUz, beamUt, beamPUx, beamPUy, beamPUz, beamPUt, beamU1, beamU2, beamU3, beamN, beamQ12, beamQ13, beamM2, beamM3):
                    # print ('YUt') 
                    
                    # add filters in here if necessary
                    bPhaseName.append(phase.Name.value)
                    bPhaseIdent.append(phase.Identification.value)
                    
                    bMat.append(mat)
                    bX.append(x)
                    bY.append(y)
                    bZ.append(z)
                                     
                    bUx.append(ux)
                    bUy.append(uy)
                    bUz.append(uz)
                    bUt.append(ut)
              
                    bPUx.append(pux)
                    bPUy.append(puy)
                    bPUz.append(puz)
                    bPUt.append(put)
                   
                    bU1.append(u1)
                    bU2.append(u2)
                    bU3.append(u3)
                    
                    bN.append(n)
                    
                    bQ12.append(q12)
                    bQ13.append(q13)
                    
                    bM2.append(m2)                    
                    bM3.append(m3)                  
                     
            except:
                print ('Exception reading beam in phase' + phase.Name.value)

        columns ='Phase,PhaseIdent,MaterialID,X(m),Y(m),Z(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N(kN/m),Q12(kN/m),Q13(kN/m),M2(kNm/m),M3(kNm/m)'
        formats = '{},{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, mat, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3)
                                 for pname, pident, mat, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(bPhaseName, bPhaseIdent, bMat, bX, bY, bZ, bUx, bUy, bUz, bUt, bPUx, bPUy, bPUz, bPUt, bU1, bU2, bU3, bN, bQ12, bQ13, bM2, bM3)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, mat, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3)
                                 for pname, pident, mat, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(bPhaseName, bPhaseIdent, bMat, bX, bY, bZ, bUx, bUy, bUz, bUt, bPUx, bPUy, bPUz, bPUt, bU1, bU2, bU3, bN, bQ12, bQ13, bM2, bM3)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, mat, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(bPhaseName, bPhaseIdent, bMat, bX, bY, bZ, bUx, bUy, bUz, bUt, bPUx, bPUy, bPUz, bPUt, bU1, bU2, bU3, bN, bQ12, bQ13, bM2, bM3):
                row= []
                row.append(pname) 
                row.append(pident)
                row.append(mat)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n)
                row.append(q12)
                row.append(q13)
                row.append(m2)
                row.append(m3)
                self.insertValues(row)
        
        print('getBeamResults Done')     
    def getEmbeddedBeamResults(self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):
# file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_EmbeddedBeam.html
        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getEmbeddedBeamResults'  
        
        print('FileOut=', fileOut)

        # init data for lists
        PhaseName = []
        PhaseIdent = []
           
        eY = []
        eX = []
        eZ = []
        
        eMat = []
        
        eUx = []
        eUy = []
        eUz = []
        eUt = []

        ePUx = []
        ePUy = []
        ePUz = []
        ePUt = []

        eU1 = []
        eU2 = []
        eU3 = []
        
        eN = []
        eQ12 = []
        eQ13 = []
        eM2 = []
        eM3 = []

        eTskin = []
        eTlat = []
        eTlat2 = []
        eFfoot = []
        
        for phase in self.phaseOrder:

            print('Getting EmbeddedBeam results for Phase ',  phase.Name.value)
            
            try:
                embeamX = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.X, 'node')
                embeamY = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Y, 'node')
                embeamZ = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Z, 'node')
                print('Retrieved U')
                ebeamMat = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.MaterialID, 'node')
                                
                embeamUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Ux, 'node')
                embeamUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Uy, 'node')
                embeamUz = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Uz, 'node')
                embeamUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Utot, 'node')
                print('Retrieved U')
                embeamPUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUx, 'node')
                embeamPUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUy, 'node')
                embeamPUz = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUz, 'node')
                embeamPUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUtot, 'node')
                print('Retrieved dU')
                embeamU1 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.U1, 'node')
                embeamU2 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.U2, 'node')
                embeamU3 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.U3, 'node')
                #print('Retrieved U1-U3')
                embeamN = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.N, 'node')
                embeamQ12 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Q12, 'node')
                embeamQ13 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Q13, 'node')
                embeamM2 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.M2, 'node')
                embeamM3 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.M3, 'node')
                #print('Retrieved N')
                embeamTskin = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tskin, 'node')
                embeamTlat= self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tlat, 'node')
                embeamTlat2= self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tlat2, 'node')
                #embeamFfoot= self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tlat2, 'node')
                
                print('Retrieved EmbeddedBeam results for ', phase.Name.value)
                
                for x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(
                        embeamX, embeamY, embeamZ, ebeamMat, embeamUx, embeamUy, embeamUz, embeamUt, embeamPUx, embeamPUy,  embeamPUz, embeamPUt, embeamU1, embeamU2, embeamU3, embeamN, embeamQ12, embeamQ13, embeamM2, embeamM3, embeamTskin, embeamTlat, embeamTlat2):
                    # add filters in here if necessary
                    PhaseName.append(phase.Name.value)
                    PhaseIdent.append(phase.Identification.value)
                    eX.append(x)
                    eY.append(y)
                    eZ.append(z)
                    eMat.append(mat)
                    eUx.append(ux)
                    eUy.append(uy)
                    eUz.append(uz)
                    eUt.append(ut)
                    ePUx.append(pux)
                    ePUy.append(puy)
                    ePUz.append(puz)
                    ePUt.append(put)
                    eU1.append(u1)
                    eU2.append(u2)
                    eU3.append(u3)
                    eN.append(n)  
                    eQ12.append(q12)
                    eQ13.append(q13)
                    eM2.append(m2)
                    eM3.append(m3)
                    eTskin.append(tskin)
                    eTlat.append(tlat)
                    eTlat2.append(tlat2)
            except:
                print ('Exception reading EmbeddedBeam in phase' + phase.Name.value)
        
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N(kN),Q12(kN),Q13(kN),M2(kNm),M3(kNm),Tskin(kN/m),Tlat(kN/m),Tlat2(kN/m)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat,ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                 for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat,ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                 for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2):
                row = []        
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n)
                row.append(q12)
                row.append(q13)
                row.append(m2)
                row.append(m3)
                row.append(tskin)
                row.append(tlat)
                row.append(tlat2)
                self.insertValues(row)
                
        print('getEmbeddedBeamResults Done')
        
    def getNodeToNodeAnchorResults(self,
                                   fileOut=None,
                                   tableOut=None,
                                   sphaseOrder=None,
                                   sphaseStart=None,
                                   sphaseEnd=None,
                                   ):
        #file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_NodeToNodeAnchor.html
        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
            
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getNodeToNodeAnchorResults'  
        
        print('FileOut=', fileOut)

        # initialize data for lists
        aPhaseName = []
        aPhaseIdent = []
        
        aY = []
        aX = []
        aZ = []
                
        aUx = []
        aUy = []
        aUz = []
        aUt = []
        
        aPUx = []
        aPUy = []
        aPUz = []
        aPUt = []
        
        aU1 = []
        aU2 = []
        aU3 = []
        
        aForce3D = []

        for phase in self.phaseOrder:

            print('Getting NodeToNodeAnchor results for Phase ', phase.Name.value, phase.Identification.value)
            try:
                anchorX = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.X, 'node')
                anchorY = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Y, 'node')
                anchorZ = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Z, 'node')
                
                anchorUx = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Ux, 'node')
                anchorUy = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Uy, 'node')
                anchorUz = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Uz, 'node')
                anchorUt = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.Utot, 'node')

                anchorPUx = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUx, 'node')
                anchorPUy = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUy, 'node')
                anchorPUz = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUz, 'node')
                anchorPUt = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.PUtot, 'node')

                anchorU1 = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.U1, 'node')
                anchorU2 = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.U2, 'node')
                anchorU3 = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.U3, 'node')
                
                anchorForce3D = self.g_o.getresults(phase, self.g_o.NodeToNodeAnchor.AnchorForce3D, 'node')

                for x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3D in zip(
                        anchorX, anchorY, anchorZ, anchorUx, anchorUy, anchorUz, anchorUt, anchorPUx, anchorPUy, anchorPUz, anchorPUt, anchorU1, anchorU2, anchorU3, anchorForce3D):
                    # add filters in here if necessary
                    aPhaseName.append(phase.Name.value)
                    aPhaseIdent.append(phase.Identification.value)
                    
                    aX.append(x)
                    aY.append(y)
                    aZ.append(z)
                                        
                    aUx.append(ux)
                    aUy.append(uy)
                    aUz.append(uz)
                    aUt.append(ut)
                    
                    aPUx.append(pux)
                    aPUy.append(puy)
                    aPUz.append(puz)
                    aPUt.append(put)
                    
                    aU1.append(u1)
                    aU2.append(u2)
                    aU3.append(u3)   
                    
                    aForce3D.append(f3D)
            except:
                 print ('Exception reading  NodeToNodeAnchor in phase' + phase.Name.value, phase.Identification.value)
        
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUtot(m),U1(m),U2(m),U3(m),N(kN)'
        formats = '{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d)
                                 for pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d in zip(aPhaseName, aPhaseIdent, aX, aY, aZ, aUx, aUy, aUz, aUt, aPUx, aPUy, aPUz, aPUt, aU1, aU2, aU3, aForce3D)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d)
                                 for pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d in zip(aPhaseName, aPhaseIdent, aX, aY, aZ, aUx, aUy, aUz, aUt, aPUx, aPUy, aPUz, aPUt, aU1, aU2, aU3, aForce3D)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d in zip(aPhaseName, aPhaseIdent, aX, aY, aZ, aUx, aUy, aUz, aUt, aPUx, aPUy, aPUz, aPUt, aU1, aU2, aU3, aForce3D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(f3d)
                self.insertValues(row)
        print('getNodeToNodeAnchorResults Done')
   
    def getFixedEndAnchorResults(self,
                                 fileOut=None,
                                 tableOut=None,
                                 sphaseOrder=None,
                                 sphaseStart=None,
                                 sphaseEnd=None
                                 ):
        # file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_FixedEndAnchor.html
        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
                
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getFixedEndAnchorResults'  
        
        print('FileOut=', fileOut)

        # initialize data for lists
        aPhaseName = []
        aPhaseIdent = []

        aY = []
        aX = []
        aZ = []
        
        aUx = []
        aUy = []
        aUz = []
        aUt = []
        
        aPUx = []
        aPUy = []
        aPUz = []
        aPUt = []
        
        aU1 = []
        aU2 = []
        aU3 = []
        
        aForce3D = []

        for phase in self.phaseOrder:

            print('Getting FixedEndAnchor results for ', phase.Name.value)
            try:
                anchorX = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.X, 'node')
                anchorY = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Y, 'node')
                anchorZ = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Z, 'node')
                
                anchorUx = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Ux, 'node')
                anchorUy = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Uy, 'node')
                anchorUz = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Uz, 'node')
                anchorUt = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.Utot, 'node')

                anchorPUx = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUx, 'node')
                anchorPUy = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUy, 'node')
                anchorPUz = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUz, 'node')
                anchorPUt = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.PUtot, 'node')

                anchorU1 = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.U1, 'node')
                anchorU2 = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.U2, 'node')
                anchorU3 = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.U3, 'node')
                
                anchorForce3D = self.g_o.getresults(phase, self.g_o.FixedEndAnchor.AnchorForce3D, 'node')
                
                print('Retrieved FixedEndAnchor results for ', phase.Name.value)
          
                for x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3D in zip(
                        anchorX, anchorY, anchorZ, anchorUx, anchorUy, anchorUz, anchorUt, anchorPUx, anchorPUy, anchorPUz, anchorPUt, anchorU1, anchorU2, anchorU3, anchorForce3D):
                    # add filters in here if necessary
                    aPhaseName.append(phase.Name.value)
                    aPhaseIdent.append(phase.Identification.value)
                    
                    aX.append(x)
                    aY.append(y)
                    aZ.append(z)
                                         
                    aUx.append(ux)
                    aUy.append(uy)
                    aUz.append(uz)
                    aUt.append(ut)
                    
                    aPUx.append(pux)
                    aPUy.append(puy)
                    aPUz.append(puz)
                    aPUt.append(put)
                    
                    aU1.append(u1)
                    aU2.append(u2)
                    aU3.append(u3)
                    
                    aForce3D.append(f3D)
            except:
                print ('Exception reading  FixedEndAnchor in phase' + phase.Name.value)
                
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUtot(m),U1(m),U2(m),U3(m),N(kN)'
        formats = '{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d)
                                 for pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d in zip(aPhaseName, aPhaseIdent, aX, aY, aZ, aUx, aUy, aUz, aUt, aPUx, aPUy, aPUz, aPUt, aU1, aU2, aU3, aForce3D)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d)
                                 for pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d in zip(aPhaseName, aPhaseIdent, aX, aY, aZ, aUx, aUy, aUz, aUt, aPUx, aPUy, aPUz, aPUt, aU1, aU2, aU3, aForce3D)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, f3d in zip(aPhaseName, aPhaseIdent, aX, aY, aZ, aUx, aUy, aUz, aUt, aPUx, aPUy, aPUz, aPUt, aU1, aU2, aU3, aForce3D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(f3d)
                self.insertValues(row)
                
        print('getFixedEndAnchorResults Done')

    def getInterfaceResults(self,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
        # file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_Interface.html
        
        self.setPhaseOrder(sphaseOrder,
           sphaseStart,
           sphaseEnd)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResults' 
        print('FileOut=', fileOut)
        
        # initialize data for lists
        iPhaseName = []
        iPhaseIdent = []

        iY = []
        iX = []
        iZ = []
        
        iMat = []
               
        iUx = []
        iUy = []
        iUz = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUz = []
        iPUt = []

        iU1 = []
        iU2 = []
        iU3 = []
        
        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            try:
                interX = self.g_o.getresults(phase, self.g_o.Interface.X, 'node')
                interY = self.g_o.getresults(phase, self.g_o.Interface.Y, 'node')
                interZ = self.g_o.getresults(phase, self.g_o.Interface.Z, 'node')
                
                interMat = self.g_o.getresults(phase, self.g_o.Interface.MaterialID, 'node')
                               
                interUx = self.g_o.getresults(phase, self.g_o.Interface.Ux, 'node')
                interUy = self.g_o.getresults(phase, self.g_o.Interface.Uy, 'node')
                interUz = self.g_o.getresults(phase, self.g_o.Interface.Uz, 'node')
                interUt = self.g_o.getresults(phase, self.g_o.Interface.Utot, 'node')

                interPUx = self.g_o.getresults(phase, self.g_o.Interface.PUx, 'node')
                interPUy = self.g_o.getresults(phase, self.g_o.Interface.PUy, 'node')
                interPUz = self.g_o.getresults(phase, self.g_o.Interface.PUz, 'node')
                interPUt = self.g_o.getresults(phase, self.g_o.Interface.PUtot, 'node')

                interU1 = self.g_o.getresults(phase, self.g_o.Interface.U1, 'node')
                interU2 = self.g_o.getresults(phase, self.g_o.Interface.U2, 'node')
                interU3 = self.g_o.getresults(phase, self.g_o.Interface.U3, 'node')
                
                interEffNormalStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceEffectiveNormalStress, 'node')
                interTotNormalStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceTotalNormalStress, 'node')
                interShearStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceShearStress, 'node')
                interRelShearStress = self.g_o.getresults(phase, self.g_o.Interface.InterfaceRelativeShearStress, 'node')

                interPExcess = self.g_o.getresults(phase, self.g_o.Interface.PExcess, 'node')
                interPActive = self.g_o.getresults(phase, self.g_o.Interface.PActive, 'node')
                interPSteady = self.g_o.getresults(phase, self.g_o.Interface.PSteady, 'node')
                interPWater = self.g_o.getresults(phase, self.g_o.Interface.PWater, 'node')
                
                interSuction = self.g_o.getresults(phase, self.g_o.Interface.Suction, 'node')
                interEffSuction = self.g_o.getresults(phase, self.g_o.Interface.EffSuction, 'node')

                for x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(
                        interX, interY, interZ, interMat, 
                        interUx, interUy, interUz, interUt, 
                        interPUx, interPUy, interPUz, interPUt, 
                        interU1, interU2, interU3,
                        interEffNormalStress, interTotNormalStress, interShearStress, interRelShearStress,
                        interPExcess, interPActive, interPSteady, interPWater, 
                        interSuction,  interEffSuction):
                    # add filters in here if necessary
                    
                    iPhaseName.append(phase.Name.value)
                    iPhaseIdent.append(phase.Identification.value)
                    
                    iX.append(x)
                    iY.append(y)
                    iZ.append(z)
                    
                    iMat.append(mat)
                                        
                    iUx.append(ux)
                    iUy.append(uy)
                    iUz.append(uz)
                    iUt.append(ut)
                    
                    iPUx.append(pux)
                    iPUy.append(puy)
                    iPUz.append(puz)
                    iPUt.append(put)
                    
                    iU1.append(u1)
                    iU2.append(u2)
                    iU3.append(u3)
                     
                    iEffNormalStress.append(ens)
                    iTotNormalStress.append(tns)
                    iShearStress.append(ss)
                    iRelShearStress.append(rss)
                    iPExcess.append(pe)
                    iPActive.append(pa)
                    iPSteady.append(pst)
                    iPWater.append(pw)
                    iSuction.append(su)
                    iEffSuction.append(esu)
            except :
                print ('Exception reading Interface results in phase' + phase.Name.value)
                    
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                in zip(iPhaseName, iPhaseIdent, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                in zip(iPhaseName, iPhaseIdent, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(ens)
                row.append(tns)
                row.append(ss)
                row.append(rss)
                row.append(pe)
                row.append(pa)
                row.append(pst)
                row.append(pw)
                row.append(su)
                row.append(esu)
                self.insertValues(row)
                
        print('getInterfaceResults Done')   
        
    def getAllStructuralResults(self,
                    folderOut=None,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):    
        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getBeamResults.csv'
        else:
            tableOut = 'getBeamResults'                
        self.getBeamResults (fileOut=fileOut, tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getPlateResults.csv'
        else:
            tableOut = 'getPlateResults'                
        self.getPlateResults (fileOut=fileOut, tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
        
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getEmbeddedBeamResults.csv'
        else:
            tableOut = 'getEmbeddedBeamResults'  
        self.getEmbeddedBeamResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )

        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getNodeToNodeAnchorResults.csv'
        else:
            tableOut = 'getNodeToNodeAnchorResults' 
        self.getNodeToNodeAnchorResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                       )
                       
   
        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getFixedEndAnchorResults.csv'
            tableOut = None
        else:
            tableOut = 'getFixedEndAnchorResults'
        
        self.getFixedEndAnchorResults (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                      )

        if (self.IsDbFile(fileOut) == False):
            fileOut = folderOut + r'\getInterfaceResults.csv'
        else:
            tableOut = 'getInterfaceResults'
        self.getInterfaceResults  (fileOut=fileOut,tableOut=tableOut,
                       sphaseOrder=sphaseOrder,
                       sphaseStart=sphaseStart,
                       sphaseEnd=sphaseEnd
                      )



class Plaxis2dResults2016 (Plaxis2dResults):
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis2dResults2016, self).__init__(server, host, port, password=password)
    def version (self):
        return "Plaxis2d2016"

    def getPlateResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResults'
        
        # init data for lists
        pPhaseName = []
        pPhaseIdent = []
           
        pY = []
        pX = []
        
        pMat = []
          
        pUx = []
        pUy = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUt = []

        pU1 = []
        pU2 = []

        pM2D = []
        pQ2D = []
        pNx2D = []
        pNz2D = []



        for phase in self.phaseOrder:
            print('Getting Plate results ' + phase.Identification.value)
            
            try: 
                plateX = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.X, 'node')
                plateY = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Y, 'node')
                
                plateMat = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.MaterialID, 'node')
                      
                plateUx = self.g_o.getresults(phase, self.g_o.Plate.Ux, 'node')
                plateUy = self.g_o.getresults(phase, self.g_o.Plate.Uy, 'node')
                plateUt = self.g_o.getresults(phase, self.g_o.Plate.Utot, 'node')

                platePUx = self.g_o.getresults(phase, self.g_o.Plate.PUx, 'node')
                platePUy = self.g_o.getresults(phase, self.g_o.Plate.PUy, 'node')
                platePUt = self.g_o.getresults(phase, self.g_o.Plate.PUtot, 'node')

                plateU1 = self.g_o.getresults(phase, self.g_o.Plate.U1, 'node')
                plateU2 = self.g_o.getresults(phase, self.g_o.Plate.U2, 'node')

                plateM2D = self.g_o.getresults(phase, self.g_o.Plate.M2D, 'node')
                plateQ2D = self.g_o.getresults(phase, self.g_o.Plate.Q2D, 'node')
                plateNx2D = self.g_o.getresults(phase, self.g_o.Plate.Nx2D, 'node')
                plateNz2D = self.g_o.getresults(phase, self.g_o.Plate.Nz2D, 'node')
                
                print('...read Plate results ' + phase.Identification.value)
                
                for x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(
                        plateX, plateY, plateMat, plateUx, plateUy, plateUt, platePUx, platePUy, platePUt, plateU1, plateU2, plateM2D, plateQ2D, plateNx2D, plateNz2D):
                    # add filters in here if necessary
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
                    pX.append(x)
                    pY.append(y)
                    pMat.append(mat)
                    pUx.append(ux)
                    pUy.append(uy)
                    pUt.append(ut)
                    pPUx.append(pux)
                    pPUy.append(puy)
                    pPUt.append(put)
                    pU1.append(u1)
                    pU2.append(u2)
                    pM2D.append(m2d)
                    pQ2D.append(q2d)
                    pNx2D.append(nx2d)
                    pNz2D.append(nz2d)
                    
            except:
                print ('...exception reading Plate results ' + phase.Identification.value)
        columns ='Phase,PhaseIdent,X(m),Y(m),MaterialID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),M2D(kNm/m),Q2D(kN/m),Nx2D(kN/m),Nz2D(kN/m)'
        formats = '{},{},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines(columns)
                file.writelines([formats.format(pname, pident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d)
                                 for pname, pident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(m2d)
                row.append(q2d)
                row.append(nx2d)
                row.append(nz2d)
                
                self.insertValues(row)
                
        print('getPlateResults Done')
        
    def getEmbeddedBeamRowResults(self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getEmbeddedBeamRowResults'
        
        # init data for lists
        ePhaseName = []
        ePhaseIdent = []
           
        eY = []
        eX = []
        
        eMat = []
            
        eUx = []
        eUy = []
        eUt = []

        ePUx = []
        ePUy = []
        ePUt = []

        eU1 = []
        eU2 = []

        eM2D = []
        eQ2D = []
        eNx2D = []
        eNz2D = []

        eTskin = []
        eTlat= []

        for phase in self.phaseOrder:
            #echo ResultTypes.EmbeddedBeamRow
            print ('Getting EmbeddedBeamRow results ' + phase.Identification.value)
            try:
                embeamX = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.X, 'node')
                embeamY = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Y, 'node')
                
                embeamMat = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.MaterialID, 'node')
                
                embeamUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Ux, 'node')
                embeamUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Uy, 'node')
                embeamUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Utot, 'node')
                
                embeamPUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.PUx, 'node')
                embeamPUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.PUy, 'node')
                embeamPUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.PUtot, 'node')
                 
                embeamU1 = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.U1, 'node')
                embeamU2 = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.U2, 'node')

                embeamM2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.M2D, 'node')
                embeamQ2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Q2D, 'node')
                embeamNx2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Nx2D, 'node')
                embeamNz2D = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Nz2D, 'node')

                embeamTskin = self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Tskin, 'node')
                embeamTlat= self.g_o.getresults(phase, self.g_o.EmbeddedBeamRow.Tlat, 'node')
                     
                print ('...read EmbeddedBeamRow results ' + phase.Identification.value)
                
                for x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(
                        embeamX, embeamY, embeamMat, embeamUx, embeamUy, embeamUt, embeamPUx, embeamPUy, embeamPUt, embeamU1, embeamU2, embeamM2D, embeamQ2D, embeamNx2D, embeamNz2D, embeamTskin, embeamTlat):
                    # add filters in here if necessary
                    
                    ePhaseName.append(phase.Name.value)
                    ePhaseIdent.append(phase.Identification.value)
                    eX.append(x)
                    eY.append(y)
                    eMat.append(mat)
                    eUx.append(ux)
                    eUy.append(uy)
                    eUt.append(ut)
                    ePUx.append(pux)
                    ePUy.append(puy)
                    ePUt.append(put)
                    eU1.append(u1)
                    eU2.append(u2)
                    eM2D.append(m2d)
                    eQ2D.append(q2d)
                    eNx2D.append(nx2d)
                    eNz2D.append(nz2d)
                    eTskin.append(tskin)
                    eTlat.append(tlat)
            except:
                print ('...exception reading EmbeddedBeamRow '  + phase.Identification.value)
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),M2D(kNm/m),Q2D(kN/m),Nx2D(kN/m),Nz2D(kN/m),Tskin(kN/m),Tlat(kN/m)'
        formats = '{},{},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat)
                                 for ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat):
                row = []
                row.append(ename)
                row.append(eident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(m2d)
                row.append(q2d)
                row.append(nx2d)
                row.append(nz2d)
                row.append(tskin)
                row.append(tlat)
                
                self.insertValues(row)
    def getSoilResultsByRange(self,
                              fileOut=None,
                              tableOut=None,
                              sphaseOrder=None,
                              sphaseStart=None,
                              sphaseEnd=None,
                              xMin=None, xMax=None,
                              yMin=None, yMax=None,
                              ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
                           
        self.setRange(xMin, xMax,
                      yMin, yMax)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByRange'  
 
        locY = []
        locX = []
        
        Uyy = []
        Uxx = []
        Utot = []
            
        PUyy = []
        PUxx = []
        PUtot = []
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []        
        
        PExcess = []
        PActive = []
        PSteady = []
        PWater = []
        
        Suct = []
        EffSuct = []
        
        pPhaseName = []
        pPhaseIdent = []
        
        # look into all phases, all steps
        for phase in self.phaseOrder:
            print('Getting Soil results for Phase ', phase.Name.value, phase.Identification.value)
            
            soilX = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.X, 'node')
            soilY = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Y, 'node')
            
            soilUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Ux, 'node')
            soilUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Uy, 'node')
            soilUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.Utot, 'node')
            
            soilPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUx, 'node')
            soilPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUy, 'node')
            soilPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.PUtot, 'node')
            
            soilEffSxx = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigxxE, 'node')
            soilEffSyy = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigyyE, 'node')
            soilEffSzz = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigzzE, 'node')
            
            soilEffP1= self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective1, 'node')
            soilEffP2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective2, 'node')
            soilEffP3 = self.g_o.getresults(phase, self.g_o.ResultTypes.Soil.SigmaEffective3, 'node')  
            
            soilPExcess = self.g_o.getresults(phase, self.g_o.Soil.PExcess, 'node')
            soilPActive = self.g_o.getresults(phase, self.g_o.Soil.PActive, 'node')
            soilPSteady = self.g_o.getresults(phase, self.g_o.Soil.PSteady, 'node')
            soilPWater = self.g_o.getresults(phase, self.g_o.Soil.PWater, 'node')
            
            soilSuction = self.g_o.getresults(phase, self.g_o.Soil.Suction, 'node')
            soilEffSuction = self.g_o.getresults(phase, self.g_o.Soil.EffSuction, 'node')
            
            for x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(
                soilX, soilY, soilUx, soilUy, soilUt, soilPUx, soilPUy, soilPUt, soilEffSxx, soilEffSyy, soilEffSzz, soilEffP1, soilEffP2, soilEffP3, soilPExcess, soilPActive, soilPSteady, soilPWater, soilSuction, soilEffSuction):
                
                if self.inRange (x_val = x, 
                                 y_val = y) == True:
                    
                    print(phase.Name.value, phase.Identification.value, x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu)
          
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
           
                    locX.append(x)
                    locY.append(y)
                    
                    Uyy.append (uy)
                    Uxx.append (ux)
                    Utot.append (ut)
            
                    PUyy.append (puy)
                    PUxx.append (pux)
                    PUtot.append (put)
                 
                    EffSxx.append(esx)
                    EffSyy.append(esy)
                    EffSzz.append(esz)
                    
                    EffP1.append (ep1)
                    EffP2.append (ep2)
                    EffP3.append (ep3)
                    
                    PExcess.append (pe)
                    PActive.append (pa)
                    PSteady.append (ps)
                    PWater.append (pw)
        
                    Suct.append (su)
                    EffSuct.append (esu)
                    
        columns = 'Phase,PhaseIdent,locX(m),locY(m),Ux(m),Uy(m),Utot(m), PUx(m), PUy(m), PUt(m), SigxxEff(kPa),SigyyEff(kPa),SigzzEff(kPa),SigP1Eff(kPa),SigyP2Eff(kPa),SigP3Eff(kPa),PExcess(kPa),PActive(kPa),PSteady(kPa),Pwater(kPa),Suct(kPa),EffSuct(kPa)'
        formats =  '{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'       
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident,  x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu )
                for pname, pident, x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(pPhaseName, pPhaseIdent, locX, locY, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct, EffSuct)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su, esu in zip(pPhaseName, pPhaseIdent, locX, locY, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct, EffSuct):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(esx)
                row.append(esy)
                row.append(esz)
                row.append(ep1)
                row.append(ep2)
                row.append(ep3)
                row.append(pe)
                row.append(pa)
                row.append(ps)
                row.append(pw)
                row.append(su)
                row.append(esu)
                
                self.insertValues(row)
                
        print('getSoilResultsByRange Done')                
           
        
    def getSoilResultsByPoints(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints'
        
        locName = []
        locY = []
        locX = []
        
        Uyy = []
        Uxx = []
        Utot = []
            
        PUyy = []
        PUxx = []
        PUtot = []
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []        
        
        PExcess = []
        PActive = []
        PSteady = []
        PWater = []
        
        Suct = []
        EffSuct = []
        
        pPhaseName = []
        pPhaseIdent = []
               

        fpoint = open(filePoints, "r")

        while True:
            in_line = fpoint.readline()
            if in_line == "":
                break
            print(in_line)
            [name, nx, ny] = in_line.split(',')
            self.NodeList.append(self.PointXY(name, nx, ny))

        fpoint.close()

       

        for phase in self.phaseOrder:
            print('Getting soil results ' + phase.Identification.value)
            

                       
            for pt in self.NodeList:

                try:
                    ux = self.g_o.getsingleresult(phase, self.g_o.Soil.Ux, (pt.x, pt.y))
                    uy = self.g_o.getsingleresult(phase, self.g_o.Soil.Uy, (pt.x, pt.y))
                    ut = self.g_o.getsingleresult(phase, self.g_o.Soil.Utot, (pt.x, pt.y))
                    pux = self.g_o.getsingleresult(phase, self.g_o.Soil.PUx, (pt.x, pt.y))
                    puy = self.g_o.getsingleresult(phase, self.g_o.Soil.PUy, (pt.x, pt.y))
                    put = self.g_o.getsingleresult(phase, self.g_o.Soil.PUtot, (pt.x, pt.y))
                    esx = self.g_o.getsingleresult(phase, self.g_o.Soil.SigxxE, (pt.x, pt.y))
                    esy = self.g_o.getsingleresult(phase, self.g_o.Soil.SigyyE, (pt.x, pt.y))
                    esz = self.g_o.getsingleresult(phase, self.g_o.Soil.SigzzE, (pt.x, pt.y))
                    ep1 = self.g_o.getsingleresult(phase, self.g_o.Soil.SigmaEffective1, (pt.x, pt.y))
                    ep2 = self.g_o.getsingleresult(phase, self.g_o.Soil.SigmaEffective2, (pt.x, pt.y))
                    ep3 = self.g_o.getsingleresult(phase, self.g_o.Soil.SigmaEffective3, (pt.x, pt.y))  
                    pe = self.g_o.getsingleresult(phase, self.g_o.Soil.PExcess, (pt.x, pt.y))
                    pa = self.g_o.getsingleresult(phase, self.g_o.Soil.PActive, (pt.x, pt.y))
                    ps = self.g_o.getsingleresult(phase, self.g_o.Soil.PSteady, (pt.x, pt.y))
                    pw = self.g_o.getsingleresult(phase, self.g_o.Soil.PWater, (pt.x, pt.y))
                    su = self.g_o.getsingleresult(phase, self.g_o.Soil.Suction, (pt.x, pt.y))
                    
                    # print (pt.name, pt.x, pt.y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su) 
                    
                    if ux != 'not found':
                    
                        pPhaseName.append(phase.Name.value)
                        pPhaseIdent.append(phase.Identification.value)
                    
                        locName.append(pt.name)
                        locY.append(pt.y)
                        locX.append(pt.x)
                        
                        Uyy.append(uy)
                        Uxx.append(ux)
                        Utot.append(ut)
                        
                        PUyy.append(puy)
                        PUxx.append(pux)
                        PUtot.append(put)
                        
                        EffSxx.append (esx)
                        EffSyy.append (esy)
                        EffSzz.append (esz)
                           
                        EffP1.append (ep1)
                        EffP2.append (ep2)
                        EffP3.append (ep3)
                            
                        PExcess.append (pe)
                        PActive.append (pa)
                        PSteady.append (ps)
                        PWater.append (pw)
                        Suct.append (su)
                     
                except:
                    print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
                    print (pt.name, pt.x, pt.y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
        columns = 'Phase,PhaseIdent,locName,locX(m),locY(m),Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),SigxxEff(kPa),SigyyEff(kPa),SigzzEff(kPa),SigP1Eff(kPa),SigyP2Eff(kPa),SigP3Eff(kPa),PExcess(kPa),PActive(kPa),PSteady(kPa),Pwater(kPa),Suct(kPa)'  
        formats = '{},{},{},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut != None and tableOut == None):
            try :
                print('Outputting to file ', fileOut, '....')
                columns += '\n'
                formats += '\n'
                with open(fileOut, "w") as file:
                    file.writelines([columns])
                    file.writelines([formats.format(pname, pident, locname, float(x), float(y), float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(esx), float(esy), float(esz), float(ep1), float(ep2), float(ep3), float(pe), float(pa), float(ps), float(pw), float(su))
                                     for pname, pident, locname, x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)])
            except:
                print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
               #~ print (pname, pident, locname, x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
                #~ print (pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, locname, x, y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(esx)
                row.append(esy)
                row.append(esz)
                row.append(ep1)
                row.append(ep2)
                row.append(ep3)
                row.append(pe)
                row.append(pa)
                row.append(ps)
                row.append(pw)
                row.append(su)
                
                self.insertValues(row)
                
        print('getSoilResultsByPoint Done')


class Plaxis2dResults2019 (Plaxis2dResults):
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis2dResults2019, self).__init__(server, host, port, password)
    def version (self):
        return "Plaxis2d2019"

    def getPlateResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResults'
        
        # init data for lists
        pPhaseName = []
        pPhaseIdent = []
           
        pY = []
        pX = []
        
        pMat = []
        pEl = []
         
        pUx = []
        pUy = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUt = []

        pU1 = []
        pU2 = []

        pM2D = []
        pQ2D = []
        pNx2D = []
        pNz2D = []



        for phase in self.phaseOrder:
            print('Getting Plate results ' + phase.Identification.value)
            
            try: 
                plateX = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.X, 'node')
                plateY = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Y, 'node')
                
                plateMat = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.MaterialID, 'node')
                plateEl = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.ElementID, 'node')      
                
                plateUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Ux, 'node')
                plateUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Uy, 'node')
                plateUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Utot, 'node')

                platePUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUx, 'node')
                platePUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUy, 'node')
                platePUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUtot, 'node')

                plateU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.U1, 'node')
                plateU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.U2, 'node')

                plateM2D = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.M2D, 'node')
                plateQ2D = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Q2D, 'node')
                plateNx2D = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Nx2D, 'node')
                plateNz2D = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Nz2D, 'node')
                
                print('...read Plate results ' + phase.Identification.value)
                
                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(
                        plateX, plateY, plateMat, plateEl, plateUx, plateUy, plateUt, platePUx, platePUy, platePUt, plateU1, plateU2, plateM2D, plateQ2D, plateNx2D, plateNz2D):
                    # add filters in here if necessary
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
                    pX.append(x)
                    pY.append(y)
                    pMat.append(mat)
                    pEl.append(el)
                    pUx.append(ux)
                    pUy.append(uy)
                    pUt.append(ut)
                    pPUx.append(pux)
                    pPUy.append(puy)
                    pPUt.append(put)
                    pU1.append(u1)
                    pU2.append(u2)
                    pM2D.append(m2d)
                    pQ2D.append(q2d)
                    pNx2D.append(nx2d)
                    pNz2D.append(nz2d)
                    
            except Exception as e:
                print ('...exception reading Plate results ' + phase.Identification.value + str(e))
                self.logger.error('...exception reading Plate results  '+ str(e))
                
        columns ='Phase,PhaseIdent,X(m),Y(m),MaterialID,ElementID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),M2D(kNm/m),Q2D(kN/m),Nx2D(kN/m),Nz2D(kN/m)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pEl, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines(columns)
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pEl, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D)])
            return "Plate results written to file:" + fileOut 
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d in zip(pPhaseName, pPhaseIdent, pX, pY, pMat, pEl, pUx, pUy, pUt, pPUx, pPUy, pPUt, pU1, pU2, pM2D, pQ2D, pNx2D, pNz2D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(m2d)
                row.append(q2d)
                row.append(nx2d)
                row.append(nz2d)
                
                self.insertValues(row)
            return "Plate results written to file:" + fileOut + " table:" + tableOut    
        print('getPlateResults Done')
       
        
    def getEmbeddedBeamRowResults(self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getEmbeddedBeamRowResults'
        
        # init data for lists
        ePhaseName = []
        ePhaseIdent = []
           
        eY = []
        eX = []
        
        eMat = []
        eEl = []
         
        eUx = []
        eUy = []
        eUt = []

        ePUx = []
        ePUy = []
        ePUt = []

        eU1 = []
        eU2 = []

        eM2D = []
        eQ2D = []
        eNx2D = []
        eNz2D = []

        eTskin = []
        eTlat= []

        for phase in self.phaseOrder:
            #echo ResultTypes.EmbeddedBeamRow
            print ('Getting EmbeddedBeamRow results ' + phase.Identification.value)
            try:
                embeamX = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.X, 'node')
                embeamY = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Y, 'node')
                
                embeamMat = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.MaterialID, 'node')
                embeamEl = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.ElementID, 'node')
                
                embeamUx = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Ux, 'node')
                embeamUy = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Uy, 'node')
                embeamUt = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Utot, 'node')
                
                embeamPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.PUx, 'node')
                embeamPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.PUy, 'node')
                embeamPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.PUtot, 'node')
                 
                embeamU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.U1, 'node')
                embeamU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.U2, 'node')

                embeamM2D = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.M2D, 'node')
                embeamQ2D = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Q2D, 'node')
                embeamNx2D = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Nx2D, 'node')
                embeamNz2D = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Nz2D, 'node')

                embeamTskin = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Tskin, 'node')
                embeamTlat= self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeamRow.Tlat, 'node')
                     
                print ('...read EmbeddedBeamRow results ' + phase.Identification.value)
                
                for x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(
                        embeamX, embeamY, embeamMat, embeamUx, embeamUy, embeamUt, embeamPUx, embeamPUy, embeamPUt, embeamU1, embeamU2, embeamM2D, embeamQ2D, embeamNx2D, embeamNz2D, embeamTskin, embeamTlat):
                    # add filters in here if necessary
                    
                    ePhaseName.append(phase.Name.value)
                    ePhaseIdent.append(phase.Identification.value)
                    eX.append(x)
                    eY.append(y)
                    eMat.append(mat)
                    eUx.append(ux)
                    eUy.append(uy)
                    eUt.append(ut)
                    ePUx.append(pux)
                    ePUy.append(puy)
                    ePUt.append(put)
                    eU1.append(u1)
                    eU2.append(u2)
                    eM2D.append(m2d)
                    eQ2D.append(q2d)
                    eNx2D.append(nx2d)
                    eNz2D.append(nz2d)
                    eTskin.append(tskin)
                    eTlat.append(tlat)
            except Exception as e:
                print ('...exception reading EmbeddedBeamRow results ' + phase.Identification.value + str(e))
                self.logger.error('...exception reading EmbeddedBeamRow results  '+ str(e))
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),M2D(kNm/m),Q2D(kN/m),Nx2D(kN/m),Nz2D(kN/m),Tskin(kN/m),Tlat(kN/m)'
        formats = '{},{},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat)
                                 for ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat)
                                 for ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for ename, eident, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, m2d, q2d, nx2d, nz2d, tskin, tlat in zip(ePhaseName, ePhaseIdent, eX, eY, eMat, eUx, eUy, eUt, ePUx, ePUy, ePUt, eU1, eU2, eM2D, eQ2D, eNx2D, eNz2D, eTskin, eTlat):
                row = []
                row.append(ename)
                row.append(eident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(m2d)
                row.append(q2d)
                row.append(nx2d)
                row.append(nz2d)
                row.append(tskin)
                row.append(tlat)
                
                self.insertValues(row)
    def getNodeToNodeAnchorResults(self,
                                   fileOut=None,
                                   tableOut=None,
                                   sphaseOrder=None,
                                   sphaseStart=None,
                                   sphaseEnd=None,
                                   ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getNodeToNodeAnchorResults'
            
        # init data for lists
        aPhaseName = []
        aPhaseIdent = []
        
        aY = []
        aX = []
        
        aMat = []
        aEl = []
        
        aUx = []
        aUy = []
        
        aPUx = []
        aPUy = []
        aPUt = []
        aUt = []
        aU1 = []
        aU2 = []
        
        aForce2D = []

        for phase in self.phaseOrder:

            print('Getting NodeToNodeAnchor results for Phase ', phase.Name.value, phase.Identification.value)
            try:
                anchorX = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.X, 'node')
                anchorY = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.Y, 'node')
                
                anchorMat = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.MaterialID, 'node')
                anchorEl = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.ElementID, 'node')
                
                anchorUx = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.Ux, 'node')
                anchorUy = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.Uy, 'node')
                anchorUt = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.Utot, 'node')

                anchorPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.PUx, 'node')
                anchorPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.PUy, 'node')
                anchorPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.PUtot, 'node')

                anchorU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.U1, 'node')
                anchorU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.U2, 'node')

                anchorForce2D = self.g_o.getresults(phase, self.g_o.ResultTypes.NodeToNodeAnchor.AnchorForce2D, 'node')

                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2D in zip(
                        anchorX, anchorY, anchorMat, anchorEl, anchorUx, anchorUy, anchorUt, anchorPUx, anchorPUy, anchorPUt, anchorU1, anchorU2, anchorForce2D):
                    # add filters in here if necessary
                    aPhaseName.append(phase.Name.value)
                    aPhaseIdent.append(phase.Identification.value)
                    aX.append(x)
                    aY.append(y)
                    aMat.append(mat)
                    aEl.append(el)
                    aUx.append(ux)
                    aUy.append(uy)
                    aUt.append(ut)
                    aPUx.append(pux)
                    aPUy.append(puy)
                    aPUt.append(put)
                    aU1.append(u1)
                    aU2.append(u2)
                    aForce2D.append(f2D)
            except Exception as e:
                print ('...exception reading NodeToNodeAnchor results ' + phase.Identification.value + str(e))
                self.logger.error('...exception reading NodeToNodeAnchor results  '+ str(e))
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),U1(m),U2(m),N(kN)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(f2d)
                
                self.insertValues(row)
                
        print('getNodeToNodeAnchorResults Done')
   
    def getFixedEndAnchorResults(self,
                                 fileOut=None,
                                 tableOut=None,
                                 sphaseOrder=None,
                                 sphaseStart=None,
                                 sphaseEnd=None
                                 ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getFixedEndAnchorResults'
        
        # init data for lists
        aPhaseName = []
        aPhaseIdent = []

        aY = []
        aX = []
        
        aMat = []
        aEl = []
        
        aUx = []
        aUy = []
        aPUx = []
        aPUy = []
        aPUt = []
        aUt = []
        aU1 = []
        aU2 = []
        
        aForce2D = []

        for phase in self.phaseOrder:

            print('Getting FixedEndAnchor results for ', phase.Name.value)
            try:
                anchorX = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.X, 'node')
                anchorY = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.Y, 'node')
                
                anchorMat = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.MaterialID, 'node')
                anchorEl = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.ElementID, 'node')
                
                anchorUx = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.Ux, 'node')
                anchorUy = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.Uy, 'node')
                anchorUt = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.Utot, 'node')

                anchorPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.PUx, 'node')
                anchorPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.PUy, 'node')
                anchorPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.PUtot, 'node')

                anchorU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.U1, 'node')
                anchorU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.U2, 'node')

                anchorForce2D = self.g_o.getresults(phase, self.g_o.ResultTypes.FixedEndAnchor.AnchorForce2D, 'node')
                
                print('Retrieved FixedEndAnchor results for ', phase.Name.value)
          
                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2D in zip(
                        anchorX, anchorY, anchorMat, anchorEl, anchorUx, anchorUy, anchorUt, anchorPUx, anchorPUy, anchorPUt, anchorU1, anchorU2, anchorForce2D):
                    # add filters in here if necessary
                    aPhaseName.append(phase.Name.value)
                    aPhaseIdent.append(phase.Identification.value)
                    aX.append(x)
                    aY.append(y)
                    aMat.append(mat)
                    aEl.append(el)
                    aUx.append(ux)
                    aUy.append(uy)
                    aUt.append(ut)
                    aPUx.append(pux)
                    aPUy.append(puy)
                    aPUt.append(put)
                    aU1.append(u1)
                    aU2.append(u2)
                    aForce2D.append(f2D)
            except Exception as e:
                print ('...exception reading FixedEndAnchor results ' + phase.Identification.value + str(e))
                self.logger.error('...exception reading FixedEndAnchor results  '+ str(e))
        columns = 'Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),U1(m),U2(m),N(kN)'
        formats = '{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, f2d in zip(aPhaseName, aPhaseIdent, aX, aY, aMat, aEl, aUx, aUy, aUt, aPUx, aPUy, aPUt, aU1, aU2, aForce2D):
                 row = []
                 row.append(pname)
                 row.append(pident)
                 row.append(x)
                 row.append(y)
                 row.append(mat)
                 row.append(el)
                 row.append(ux)
                 row.append(uy)
                 row.append(ut)
                 row.append(pux)
                 row.append(puy)
                 row.append(put)
                 row.append(u1)
                 row.append(u2)
                 row.append(f2d)
                 
                 self.insertValues(row)
                 
        print('getFixedEndAnchorResults Done')
    def getInterfaceResults(self,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
        self.setPhaseOrder(sphaseOrder,
           sphaseStart,
           sphaseEnd)
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResults'
        
        # init data for lists
        iPhaseName = []
        iPhaseIdent = []

        iY = []
        iX = []
        iMat = []
        iEl = []
        
        iUx = []
        iUy = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUt = []

        iU1 = []
        iU2 = []

        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            try:
                interX = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.X, 'node')
                interY = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Y, 'node')
              
                interMat = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.MaterialID, 'node')
                interEl = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.ElementID, 'node')
              
                interUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Ux, 'node')
                interUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Uy, 'node')
                interUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Utot, 'node')

                interPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUx, 'node')
                interPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUy, 'node')
                interPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUtot, 'node')

                interU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.U1, 'node')
                interU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.U2, 'node')

                interEffNormalStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceEffectiveNormalStress, 'node')
                interTotNormalStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceTotalNormalStress, 'node')
                interShearStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceShearStress, 'node')
                interRelShearStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceRelativeShearStress, 'node')

                interPExcess = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PExcess, 'node')
                interPActive = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PActive, 'node')
                interPSteady = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PSteady, 'node')
                interPWater = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PWater, 'node')
                
                interSuction = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Suction, 'node')
                interEffSuction = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.EffSuction, 'node')

                for x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(
                        interX, interY, interMat, interEl, 
                        interUx, interUy, interUt, 
                        interPUx, interPUy, interPUt, 
                        interU1, interU2, 
                        interEffNormalStress, interTotNormalStress, interShearStress, interRelShearStress,
                        interPExcess, interPActive, interPSteady, interPWater, 
                        interSuction,  interEffSuction):
                    # add filters in here if necessary
                    iPhaseName.append(phase.Name.value)
                    iPhaseIdent.append(phase.Identification.value)
                    iX.append(x)
                    iY.append(y)
                    iMat.append(mat)
                    iEl.append(el)
                    iUx.append(ux)
                    iUy.append(uy)
                    iUt.append(ut)
                    iPUx.append(pux)
                    iPUy.append(puy)
                    iPUt.append(put)
                    iU1.append(u1)
                    iU2.append(u2)
                    iEffNormalStress.append(ens)
                    iTotNormalStress.append(tns)
                    iShearStress.append(ss)
                    iRelShearStress.append(rss)
                    iPExcess.append(pe)
                    iPActive.append(pa)
                    iPSteady.append(pst)
                    iPWater.append(pw)
                    iSuction.append(su)
                    iEffSuction.append(esu)
            except Exception as e:
                print ('...exception reading Interface results ' + phase.Identification.value + str(e))
                self.logger.error('...exception reading Interface results  '+ str(e))
        
        columns = "Phase,PhaseIdent,X(m),Y(m),MaterialId,ElementId,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)"
        formats = "{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}"
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                                 in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iEl, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                                 for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                                 in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iEl, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, mat, el, ux, uy, ut, pux, puy, put, u1, u2, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iX, iY, iMat, iEl, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                                     row = []
                                     row.append(pname)
                                     row.append(pident)
                                     row.append(x)
                                     row.append(y)
                                     row.append(mat)
                                     row.append(el)
                                     row.append(ux)
                                     row.append(uy)
                                     row.append(ut)
                                     row.append(pux)
                                     row.append(puy)
                                     row.append(put)
                                     row.append(u1)
                                     row.append(u2)
                                     row.append(ens)
                                     row.append(tns)
                                     row.append(ss)
                                     row.append(rss)
                                     row.append(pe)
                                     row.append(pa)
                                     row.append(pst)
                                     row.append(pw)
                                     row.append(su)
                                     row.append(esu)
                                     self.insertValues(row)
            
        print('getInterfaceResults Done')  
        
    def getSoilResultsByPoints(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints'
        
        locName = []
        locY = []
        locX = []
        
        MaterialID = []
        ElementID =[]
        
        Uyy = []
        Uxx = []
        Utot = []
            
        PUyy = []
        PUxx = []
        PUtot = []
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []        
        
        PExcess = []
        PActive = []
        PSteady = []
        PWater = []
        
        Suct = []

        
        pPhaseName = []
        pPhaseIdent = []
               
        if filePoints:
            fpoint = open(filePoints, "r")

            while True:
                in_line = fpoint.readline()
                if in_line == "":
                    break
                print(in_line)
                [name, nx, ny] = in_line.split(',')
                self.NodeList.append(self.PointXY(name, nx, ny))

            fpoint.close()

       

        for phase in self.phaseOrder:
            print('Getting soil results ' + phase.Identification.value)
            

                       
            for pt in self.NodeList:

                try:
                    mat = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.MaterialID, (pt.x, pt.y))
                    el = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.ElementID, (pt.x, pt.y))
                    ux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Ux, (pt.x, pt.y))
                    uy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Uy, (pt.x, pt.y))
                    ut = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Utot, (pt.x, pt.y))
                    pux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUx, (pt.x, pt.y))
                    puy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUy, (pt.x, pt.y))
                    put = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUtot, (pt.x, pt.y))
                    esx = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigxxE, (pt.x, pt.y))
                    esy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigyyE, (pt.x, pt.y))
                    esz = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigzzE, (pt.x, pt.y))
                    ep1 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigmaEffective1, (pt.x, pt.y))
                    ep2 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigmaEffective2, (pt.x, pt.y))
                    ep3 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigmaEffective3, (pt.x, pt.y))  
                    pe = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PExcess, (pt.x, pt.y))
                    pa = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PActive, (pt.x, pt.y))
                    ps = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PSteady, (pt.x, pt.y))
                    pw = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PWater, (pt.x, pt.y))
                    su = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Suction, (pt.x, pt.y))
                    
                    # print (pt.name, pt.x, pt.y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su) 
                    
                    if ux != 'not found':
                    
                        pPhaseName.append(phase.Name.value)
                        pPhaseIdent.append(phase.Identification.value)
                    
                        locName.append(pt.name)
                        locY.append(pt.y)
                        locX.append(pt.x)
                        
                        MaterialID.append(int(float(mat) + .1))
                        ElementID.append(int(float(el) + .1))
                        
                        Uyy.append(uy)
                        Uxx.append(ux)
                        Utot.append(ut)
                        
                        PUyy.append(puy)
                        PUxx.append(pux)
                        PUtot.append(put)
                        
                        EffSxx.append (esx)
                        EffSyy.append (esy)
                        EffSzz.append (esz)
                           
                        EffP1.append (ep1)
                        EffP2.append (ep2)
                        EffP3.append (ep3)
                            
                        PExcess.append (pe)
                        PActive.append (pa)
                        PSteady.append (ps)
                        PWater.append (pw)
                        Suct.append (su)
                     
                except:
                    print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
                    print (pt.name, pt.x, pt.y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
        columns = 'Phase,PhaseIdent,locName,locX(m),locY(m),MaterialID,ElementID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),SigxxEff(kPa),SigyyEff(kPa),SigzzEff(kPa),SigP1Eff(kPa),SigyP2Eff(kPa),SigP3Eff(kPa),PExcess(kPa),PActive(kPa),PSteady(kPa),Pwater(kPa),Suct(kPa)'  
        formats = '{},{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, locname, float(x), float(y), mat, el, float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(esx), float(esy), float(esz), float(ep1), float(ep2), float(ep3), float(pe), float(pa), float(ps), float(pw), float(su))
                                     for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            try :
                print('Outputting to file ', fileOut, '....')
                columns += '\n'
                formats += '\n'
                with open(fileOut, "w") as file:
                    file.writelines([columns])
                    file.writelines([formats.format(pname, pident, locname, float(x), float(y), mat, el, float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(esx), float(esy), float(esz), float(ep1), float(ep2), float(ep3), float(pe), float(pa), float(ps), float(pw), float(su))
                                     for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)])
            except:
                print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
               #~ print (pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
                #~ print (pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(esx)
                row.append(esy)
                row.append(esz)
                row.append(ep1)
                row.append(ep2)
                row.append(ep3)
                row.append(pe)
                row.append(pa)
                row.append(ps)
                row.append(pw)
                row.append(su)
                
                self.insertValues(row)
                
        print('getSoilResultsByPoint Done')

class Plaxis2dResultsConnectV2 (Plaxis2dResults2019):
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis2dResultsConnectV2, self).__init__(server, host, port, password)
    def version (self):
        return "Plaxis2dConnectV2"

    def getInterfaceResultsByPointsByStep (self,
                        filePoints=None,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None,
                        stepList=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
  
        if not filePoints is None:
            self.loadXYNodeList(filePoints)
        
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResultsByPointsStep'  
        
        print('FileOut=', fileOut)

        # initialize data for lists
        iPhaseName = []
        iPhaseIdent = []
        
        iLocName = []
        
        iY = []
        iX = []
         
        iMat = []
               
        iUx = []
        iUy = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUt = []
         
        iU1 = []
        iU2 = []

        iVx = []
        iVy = []
        iVt = []
        
        iAx = []
        iAy = []
        iAt = []           

        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print("Getting Interface results for Phase:{}".format(phase.Name.value))
            
            for step in phase:
            
                if stepList is None or step.Name.value in stepList:
            
                    print("Getting Interface results for Step:{}".format(step.Name.value))
                    
                    for pt in self.NodeList:
                        
                        print("Getting Interface results for Node:{}".format(pt.name))
                        
                        try:
                           
                            x = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.X, (pt.x, pt.y))
                            y = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Y, (pt.x, pt.y))
                           
                            mat = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.MaterialID,  (pt.x, pt.y))
                                     
                            ux = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Ux, (pt.x, pt.y))
                            uy = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Uy, (pt.x, pt.y))
                            ut = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Utot, (pt.x, pt.y))

                            pux = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PUx, (pt.x, pt.y))
                            puy = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PUy, (pt.x, pt.y))
                            put = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PUtot, (pt.x, pt.y))
                            
                            u1 = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.U1, (pt.x, pt.y))
                            u2 = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.U2, (pt.x, pt.y))
                            
                            vx =  self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Vx, (pt.x, pt.y))
                            vy = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Vy, (pt.x, pt.y))
                            vt = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Vtot, (pt.x, pt.y))
                           
                            ax =  self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Ax, (pt.x, pt.y))
                            ay = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Ay, (pt.x, pt.y))
                            at = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Atot, (pt.x, pt.y))
                            
                            ens = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.InterfaceEffectiveNormalStress, (pt.x, pt.y))
                            tns = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.InterfaceTotalNormalStress, (pt.x, pt.y))
                            ss = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.InterfaceShearStress, (pt.x, pt.y))
                            rss = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.InterfaceRelativeShearStress, (pt.x, pt.y))

                            pe = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PExcess, (pt.x, pt.y))
                            pa = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PActive, (pt.x, pt.y))
                            pst = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PSteady, (pt.x, pt.y))
                            pw = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.PWater, (pt.x, pt.y))
                            
                            su = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.Suction, (pt.x, pt.y))
                            esu = self.g_o.getsingleresult(step, self.g_o.ResultTypes.Interface.EffSuction, (pt.x, pt.y))
                            
                            if ux == 'not found':
                                print("results for {} {} ({} {}) not found".format(step.Name.value, pt.name, pt.x, pt.y))
                            if ux != 'not found':
                                print("results for {} {} ({} {}) retrieved".format(step.Name.value, pt.name, pt.x, pt.y))
                                # add filters in here if necessary
                                iPhaseName.append(phase.Name.value)
                                iPhaseIdent.append(phase.Identification.value)
                                
                                iX.append(x)
                                iY.append(y)
                                
                                iMat.append(mat)
                                iLocName.append (pt.name)
                                
                                iUx.append(ux)
                                iUy.append(uy)
                             
                                iUt.append(ut)
                                
                                iPUx.append(pux)
                                iPUy.append(puy)
                                iPUt.append(put)
                                
                                iU1.append(u1)
                                iU2.append(u2)
                              
                                iVx.append(vx)
                                iVy.append(vy)
                                iVt.append(vt)
                                
                                iAx.append(ax)
                                iAy.append(ay)
                                iAt.append(at)
                                
                                iEffNormalStress.append(ens)
                                iTotNormalStress.append(tns)
                                
                                iShearStress.append(ss)
                                iRelShearStress.append(rss)
                                
                                iPExcess.append(pe)
                                iPActive.append(pa)
                                iPSteady.append(pst)
                                iPWater.append(pw)
                                iSuction.append(su)
                                iEffSuction.append(esu)
                                
                        except:
                            print ('Exception reading Interface results in phase:' + phase.Name.value + ' step:' + step.Name.value)
                            break
        columns ='Phase,PhaseIdent,LocName,X(m),Y(m),MaterialID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUt(m),U1(m),U2(m),Vx(m/s),Vy(m/s),Vt(m/s),Ax(m/s2),Ay(m/s2),At(m/s2),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)'
        formats = '{},{},{},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, loc, float(x), float(y), float(mat), float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(u1), float(u2), float(vx), float(vy), float(vt), float(ax), float(ay), float(at), float(ens), float(tns), float(ss), float(rss), float(pe), float(pa), float(pst), float(pw), float(su), float(esu))
                for pname, pident, loc, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, vx, vy, vt, ax, ay, at, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iMat, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iVx, iVy, iVt, iAx, iAy, iAt, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            
            #~ print(iLocName)
            #~ print(iPhaseName)
            #~ print(iPhaseIdent)
            #~ print(iX)
            #~ print(iY)
            #~ print(iZ)
            #~ print(iMat)
            
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, loc, float(x), float(y), float(mat), float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(u1), float(u2), float(vx), float(vy), float(vt), float(ax), float(ay), float(at), float(ens), float(tns), float(ss), float(rss), float(pe), float(pa), float(pst), float(pw), float(su), float(esu))
                for pname, pident, loc, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, vx, vy, vt, ax, ay, at, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iMat, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iVx, iVy, iVt, iAx, iAy, iAt, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, loc, x, y, mat, ux, uy, ut, pux, puy, put, u1, u2, vx, vy, vt, ax, ay, at, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iMat, iUx, iUy, iUt, iPUx, iPUy, iPUt, iU1, iU2, iVx, iVy, iVt, iAx, iAy, iAt, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(loc)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(vx)
                row.append(vy)
                row.append(vt)
                row.append(ax)
                row.append(ay)
                row.append(at)
                row.append(ens)
                row.append(tns)
                row.append(ss)
                row.append(rss)
                row.append(pe)
                row.append(pa)
                row.append(pst)
                row.append(pw)
                row.append(su)
                row.append(esu)
                self.insertValues(row)
        
        print('getInterfaceResultsByPointsByStep Done') 
    def getSoilResultsByPoints(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):
        
        NotFound = ['not found','nan','Nan']

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1

        print('FileOut=', fileOut)
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints'
        
        locName = []
        locY = []
        locX = []
        
        MaterialID = []
        ElementID =[]
        
        Uyy = []
        Uxx = []
        Utot = []
            
        PUyy = []
        PUxx = []
        PUtot = []
        
        EffSxx = []
        EffSyy = []
        EffSzz = []
        
        EffP1 = []
        EffP2 = []
        EffP3 = []        
        
        PExcess = []
        PActive = []
        PSteady = []
        PWater = []
        
        Suct = []
        EffSuct = []
        
        pPhaseName = []
        pPhaseIdent = []
               
        if filePoints:
            fpoint = open(filePoints, "r")

            while True:
                in_line = fpoint.readline()
                if in_line == "":
                    break
                print(in_line)
                [name, nx, ny] = in_line.split(',')
                self.NodeList.append(self.PointXY(name, nx, ny))

            fpoint.close()

       

        for phase in self.phaseOrder:
            print('Getting soil results ' + phase.Identification.value)
                                   
            for pt in self.NodeList:

                try:
                    mat = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.MaterialID, (pt.x, pt.y))
                    el = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.ElementID, (pt.x, pt.y))
                    ux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Ux, (pt.x, pt.y))
                    uy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Uy, (pt.x, pt.y))
                    ut = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Utot, (pt.x, pt.y))
                    pux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUx, (pt.x, pt.y))
                    puy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUy, (pt.x, pt.y))
                    put = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUtot, (pt.x, pt.y))
                    esx = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigxxE, (pt.x, pt.y))
                    esy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigyyE, (pt.x, pt.y))
                    esz = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigzzE, (pt.x, pt.y))
                    ep1 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigmaEffective1, (pt.x, pt.y))
                    ep2 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigmaEffective2, (pt.x, pt.y))
                    ep3 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.SigmaEffective3, (pt.x, pt.y))  
                    pe = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PExcess, (pt.x, pt.y))
                    pa = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PActive, (pt.x, pt.y))
                    ps = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PSteady, (pt.x, pt.y))
                    pw = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PWater, (pt.x, pt.y))
                    su = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Suction, (pt.x, pt.y))
                    
                    if phase.Name.value == 'Phase_2':
                        print (phase.Identification.value, pt.name, pt.x, pt.y, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su) 
                    
                    # for the case when the results are not values trigger an exception 
                    # before the values are added to the result lists

                    test_x_float = float(ux)
                    
                    # print (ux, test_x_float)
                    
                    if ux not in NotFound:
                    
                        pPhaseName.append(phase.Name.value)
                        pPhaseIdent.append(phase.Identification.value)
                    
                        locName.append(pt.name)
                        locY.append(pt.y)
                        locX.append(pt.x)
                        
                        MaterialID.append(int(float(mat) + .1))
                        ElementID.append(int(float(el) + .1))
                        
                        Uyy.append(uy)
                        Uxx.append(ux)
                        Utot.append(ut)
                        
                        PUyy.append(puy)
                        PUxx.append(pux)
                        PUtot.append(put)
                        
                        EffSxx.append (esx)
                        EffSyy.append (esy)
                        EffSzz.append (esz)
                           
                        EffP1.append (ep1)
                        EffP2.append (ep2)
                        EffP3.append (ep3)
                            
                        PExcess.append (pe)
                        PActive.append (pa)
                        PSteady.append (ps)
                        PWater.append (pw)
                        Suct.append (su)
               
     
                except:
                    print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
                    print (pt.name, pt.x, pt.y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
        columns = 'Phase,PhaseIdent,locName,locX(m),locY(m),MaterialID,ElementID,Ux(m),Uy(m),Utot(m),PUx(m),PUy(m),PUtot(m),SigxxEff(kPa),SigyyEff(kPa),SigzzEff(kPa),SigP1Eff(kPa),SigyP2Eff(kPa),SigP3Eff(kPa),PExcess(kPa),PActive(kPa),PSteady(kPa),Pwater(kPa),Suct(kPa)'  
        formats = '{},{},{},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to string....')
            rows = ''.join([formats.format(pname, pident, locname, float(x), float(y), mat, el, float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(esx), float(esy), float(esz), float(ep1), float(ep2), float(ep3), float(pe), float(pa), float(ps), float(pw), float(su))
                                     for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            try :
                print('Outputting to file ', fileOut, '....')
                columns += '\n'
                formats += '\n'
                with open(fileOut, "w") as file:
                    file.writelines([columns])
                    file.writelines([formats.format(pname, pident, locname, float(x), float(y), mat, el, float(ux), float(uy), float(ut), float(pux), float(puy), float(put), float(esx), float(esy), float(esz), float(ep1), float(ep2), float(ep3), float(pe), float(pa), float(ps), float(pw), float(su))
                                     for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)])
            except:
                print ('...exception soil results ' + phase.Identification.value , pt.x, pt.y)
               #~ print (pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su)
                #~ print (pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct)
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, locname, x, y, mat, el, ux, uy, ut, pux, puy, put, esx, esy, esz, ep1, ep2, ep3, pe, pa, ps, pw, su in zip(pPhaseName, pPhaseIdent, locName, locX, locY, MaterialID, ElementID, Uxx, Uyy, Utot, PUxx, PUyy, PUtot, EffSxx, EffSyy, EffSzz, EffP1, EffP2, EffP3, PExcess, PActive, PSteady, PWater, Suct):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(put)
                row.append(esx)
                row.append(esy)
                row.append(esz)
                row.append(ep1)
                row.append(ep2)
                row.append(ep3)
                row.append(pe)
                row.append(pa)
                row.append(ps)
                row.append(pw)
                row.append(su)
                
                self.insertValues(row)
                
        print('getSoilResultsByPoint Done')

class Plaxis3dResults2018 (Plaxis3dResults):
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis3dResults2018, self).__init__(server, host, port, password)
    def version (self):
        return "Plaxis3d2018"
    def getPlateResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResults'  
        print('FileOut=', fileOut)

        # initialise data for lists
        pPhaseName = []
        pPhaseIdent = []
           
        pY = []
        pX = []
        pZ = []
        
        pMat = []
        pEl = []
               
        pUx = []
        pUy = []
        pUz = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUz = []
        pPUt = []

        pU1 = []
        pU2 = []
        pU3 = []
        
        pM11 = []
        pM22 = []
        pM12 = []
        
        pQ12 = []
        pQ23 = [] 
        pQ13 = []
        
        pN1 = []
        pN2 = []



        for phase in self.phaseOrder:
            print('Getting Plate results for Phase ', phase.Name.value, phase.Identification.value)
            
            try: 
                plateX = self.g_o.getresults(phase, self.g_o.Plate.X, 'node')
                plateY = self.g_o.getresults(phase, self.g_o.Plate.Y, 'node')
                plateZ = self.g_o.getresults(phase, self.g_o.Plate.Z, 'node')
                
                plateMat = self.g_o.getresults(phase, self.g_o.Plate.MaterialID, 'node')
                plateEl = self.g_o.getresults(phase, self.g_o.Plate.ElementID, 'node')
                                
                plateUx = self.g_o.getresults(phase, self.g_o.Plate.Ux, 'node')
                plateUy = self.g_o.getresults(phase, self.g_o.Plate.Uy, 'node')
                plateUz = self.g_o.getresults(phase, self.g_o.Plate.Uz, 'node')
                plateUt = self.g_o.getresults(phase, self.g_o.Plate.Utot, 'node')

                platePUx = self.g_o.getresults(phase, self.g_o.Plate.PUx, 'node')
                platePUy = self.g_o.getresults(phase, self.g_o.Plate.PUy, 'node')
                platePUz = self.g_o.getresults(phase, self.g_o.Plate.PUz, 'node')
                platePUt = self.g_o.getresults(phase, self.g_o.Plate.PUtot, 'node')

                plateU1 = self.g_o.getresults(phase, self.g_o.Plate.U1, 'node')
                plateU2 = self.g_o.getresults(phase, self.g_o.Plate.U2, 'node')
                plateU3 = self.g_o.getresults(phase, self.g_o.Plate.U3, 'node')
                
                plateN1 = self.g_o.getresults(phase, self.g_o.Plate.N11, 'node')
                plateN2 = self.g_o.getresults(phase, self.g_o.Plate.N22, 'node')                
                plateQ12 = self.g_o.getresults(phase, self.g_o.Plate.Q12, 'node')
                plateQ23 = self.g_o.getresults(phase, self.g_o.Plate.Q23, 'node')
                plateQ13 = self.g_o.getresults(phase, self.g_o.Plate.Q13, 'node')
                plateM11 = self.g_o.getresults(phase, self.g_o.Plate.M11, 'node')
                plateM22 = self.g_o.getresults(phase, self.g_o.Plate.M22, 'node')
                plateM12 = self.g_o.getresults(phase, self.g_o.Plate.M12, 'node')
                
                for x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(
                        plateX, plateY, plateZ, plateMat, plateEl, plateUx, plateUy, plateUz, plateUt, platePUx, platePUy, platePUz, platePUt, plateU1, plateU2, plateU3, plateN1, plateN2, plateQ12, plateQ23, plateQ13, plateM11, plateM22, plateM12):
                    # add filters in here if necessary
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
                    
                    pX.append(x)
                    pY.append(y)
                    pZ.append(z)
                    pMat.append(mat)
                    pEl.append (el)
                   
                    pUx.append(ux)
                    pUy.append(uy)
                    pUz.append(uz)
                    pUt.append(ut)
                    
                    pPUx.append(pux)
                    pPUy.append(puy)
                    pPUz.append(puz)
                    pPUt.append(put)
                   
                    pU1.append(u1)
                    pU2.append(u2)
                    pU3.append(u3)
                    
                    pN1.append(n1)
                    pN2.append(n2)
                    pQ12.append(q12)
                    pQ23.append(q23)
                    pQ13.append(q13)
                    pM11.append(m11)                    
                    pM22.append(m22)                  
                    pM12.append(m12) 
            except Exception as e:
                print ('Exception reading Plate in phase' + phase.Name.value)
                self.logger.error('...exception reading Plate results  '+ str(e))
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID, ElementID, Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N1(kN/m),N2(kN/m),Q12(kN/m),Q23(kN/m),Q13(kN/m),M11(kNm/m),M22(kNm/m),M12(kNm/m)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pEl, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pEl, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            print (self.columns)
            print (self.formats)
            print (self.types)
            for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pEl, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12):
                row= []
                row.append(pname) 
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n1)
                row.append(n2)
                row.append(q12)
                row.append(q23)
                row.append(q13)
                row.append(m11)
                row.append(m22)
                row.append(m12)
                self.insertValues(row)
        
        print('getPlateResults Done')
        
    def getBeamResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getBeamResults'
        print('FileOut=', fileOut)

        # initialise data for lists
        bPhaseName = []
        bPhaseIdent = []
           
        bMat = []
        bEl =[]
        bY = []
        bX = []
        bZ = []
        
        bUx = []
        bUy = []
        bUz = []
        bUt = []

        bPUx = []
        bPUy = []
        bPUz = []
        bPUt = []

        bU1 = []
        bU2 = []
        bU3 = []
        
        bM2 = []
        bM3 = []
        
        bQ12 = []
        bQ13 = [] 
        
        bN = []
      

        for phase in self.phaseOrder:
            print('Getting Beam results for Phase ', phase.Name.value, phase.Identification.value)
            
            try: 
                beamMat = self.g_o.getresults(phase, self.g_o.Beam.MaterialID, 'node')
                beamEl = self.g_o.getresults(phase, self.g_o.Beam.ElementID, 'node') 
                beamX = self.g_o.getresults(phase, self.g_o.Beam.X, 'node')
                beamY = self.g_o.getresults(phase, self.g_o.Beam.Y, 'node')
                beamZ = self.g_o.getresults(phase, self.g_o.Beam.Z, 'node')
                
                beamUx = self.g_o.getresults(phase, self.g_o.Beam.Ux, 'node')
                beamUy = self.g_o.getresults(phase, self.g_o.Beam.Uy, 'node')
                beamUz = self.g_o.getresults(phase, self.g_o.Beam.Uz, 'node')
                beamUt = self.g_o.getresults(phase, self.g_o.Beam.Utot, 'node')

                beamPUx = self.g_o.getresults(phase, self.g_o.Beam.PUx, 'node')
                beamPUy = self.g_o.getresults(phase, self.g_o.Beam.PUy, 'node')
                beamPUz = self.g_o.getresults(phase, self.g_o.Beam.PUz, 'node')
                beamPUt = self.g_o.getresults(phase, self.g_o.Beam.PUtot, 'node')

                beamU1 = self.g_o.getresults(phase, self.g_o.Beam.U1, 'node')
                beamU2 = self.g_o.getresults(phase, self.g_o.Beam.U2, 'node')
                beamU3 = self.g_o.getresults(phase, self.g_o.Beam.U3, 'node')
                
                beamN = self.g_o.getresults(phase, self.g_o.Beam.N, 'node')
                beamQ12 = self.g_o.getresults(phase, self.g_o.Beam.Q12, 'node')
                beamQ13 = self.g_o.getresults(phase, self.g_o.Beam.Q13, 'node')
                beamM2 = self.g_o.getresults(phase, self.g_o.Beam.M2, 'node')
                beamM3 = self.g_o.getresults(phase, self.g_o.Beam.M3, 'node')
                     
                for mat, el, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(
                        beamMat, beamEl, beamX, beamY, beamZ, beamUx, beamUy, beamUz, beamUt, beamPUx, beamPUy, beamPUz, beamPUt, beamU1, beamU2, beamU3, beamN, beamQ12, beamQ13, beamM2, beamM3):
                    # print ('YUt') 
                    
                    # add filters in here if necessary
                    bPhaseName.append(phase.Name.value)
                    bPhaseIdent.append(phase.Identification.value)
                    
                    bMat.append(mat)
                    bEl.append(el)
                    bX.append(x)
                    bY.append(y)
                    bZ.append(z)
                                     
                    bUx.append(ux)
                    bUy.append(uy)
                    bUz.append(uz)
                    bUt.append(ut)
              
                    bPUx.append(pux)
                    bPUy.append(puy)
                    bPUz.append(puz)
                    bPUt.append(put)
                   
                    bU1.append(u1)
                    bU2.append(u2)
                    bU3.append(u3)
                    
                    bN.append(n)
                    
                    bQ12.append(q12)
                    bQ13.append(q13)
                    
                    bM2.append(m2)                    
                    bM3.append(m3)                  
                     
            except:
                print ('Exception reading beam in phase' + phase.Name.value)

        columns ='Phase,PhaseIdent,MaterialID,ElementID,X(m),Y(m),Z(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N(kN/m),Q12(kN/m),Q13(kN/m),M2(kNm/m),M3(kNm/m)'
        formats = '{},{},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, mat, el, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3)
                                 for pname, pident, mat, el, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(bPhaseName, bPhaseIdent, bMat, bEl, bX, bY, bZ, bUx, bUy, bUz, bUt, bPUx, bPUy, bPUz, bPUt, bU1, bU2, bU3, bN, bQ12, bQ13, bM2, bM3)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, mat, el, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3)
                                 for pname, pident, mat, el, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(bPhaseName, bPhaseIdent, bMat, bEl, bX, bY, bZ, bUx, bUy, bUz, bUt, bPUx, bPUy, bPUz, bPUt, bU1, bU2, bU3, bN, bQ12, bQ13, bM2, bM3)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, mat, el, x, y, z, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3 in zip(bPhaseName, bPhaseIdent, bMat, bEl, bX, bY, bZ, bUx, bUy, bUz, bUt, bPUx, bPUy, bPUz, bPUt, bU1, bU2, bU3, bN, bQ12, bQ13, bM2, bM3):
                row= []
                row.append(pname) 
                row.append(pident)
                row.append(mat)
                row.append(el)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n)
                row.append(q12)
                row.append(q13)
                row.append(m2)
                row.append(m3)
                self.insertValues(row)
        
        print('getBeamResults Done')

    def getEmbeddedBeamResults(self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):
# file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_EmbeddedBeam.html
        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getEmbeddedBeamResults'  
        
        print('FileOut=', fileOut)

        # init data for lists
        PhaseName = []
        PhaseIdent = []
           
        eY = []
        eX = []
        eZ = []
        
        eMat = []
        eEl = []
        
        eUx = []
        eUy = []
        eUz = []
        eUt = []

        ePUx = []
        ePUy = []
        ePUz = []
        ePUt = []

        eU1 = []
        eU2 = []
        eU3 = []
        
        eN = []
        eQ12 = []
        eQ13 = []
        eM2 = []
        eM3 = []

        eTskin = []
        eTlat = []
        eTlat2 = []
        eFfoot = []
        
        for phase in self.phaseOrder:

            print('Getting EmbeddedBeam results for Phase ',  phase.Name.value)
            
            try:
                embeamX = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.X, 'node')
                embeamY = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Y, 'node')
                embeamZ = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Z, 'node')
                #print('Retrieved U')
                ebeamMat = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.MaterialID, 'node')
                ebeamEl = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.ElementID, 'node')
                                
                embeamUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Ux, 'node')
                embeamUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Uy, 'node')
                embeamUz = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Uz, 'node')
                embeamUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Utot, 'node')
                #print('Retrieved U')
                embeamPUx = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUx, 'node')
                embeamPUy = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUy, 'node')
                embeamPUz = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUz, 'node')
                embeamPUt = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.PUtot, 'node')
                #print('Retrieved dU')
                embeamU1 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.U1, 'node')
                embeamU2 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.U2, 'node')
                embeamU3 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.U3, 'node')
                #print('Retrieved U1-U3')
                embeamN = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.N, 'node')
                embeamQ12 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Q12, 'node')
                embeamQ13 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Q13, 'node')
                embeamM2 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.M2, 'node')
                embeamM3 = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.M3, 'node')
                #print('Retrieved N')
                embeamTskin = self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tskin, 'node')
                embeamTlat= self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tlat, 'node')
                embeamTlat2= self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tlat2, 'node')
                #embeamFfoot= self.g_o.getresults(phase, self.g_o.EmbeddedBeam.Tlat2, 'node')
                
                print('Retrieved EmbeddedBeam results for ', phase.Name.value)
                
                for x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(
                        embeamX, embeamY, embeamZ, ebeamMat, ebeamEl, embeamUx, embeamUy, embeamUz, embeamUt, embeamPUx, embeamPUy,  embeamPUz, embeamPUt, embeamU1, embeamU2, embeamU3, embeamN, embeamQ12, embeamQ13, embeamM2, embeamM3, embeamTskin, embeamTlat, embeamTlat2):
                    # add filters in here if necessary
                    PhaseName.append(phase.Name.value)
                    PhaseIdent.append(phase.Identification.value)
                    eX.append(x)
                    eY.append(y)
                    eZ.append(z)
                    eMat.append(mat)
                    eEl.append(el)
                    eUx.append(ux)
                    eUy.append(uy)
                    eUz.append(uz)
                    eUt.append(ut)
                    ePUx.append(pux)
                    ePUy.append(puy)
                    ePUz.append(puz)
                    ePUt.append(put)
                    eU1.append(u1)
                    eU2.append(u2)
                    eU3.append(u3)
                    eN.append(n)  
                    eQ12.append(q12)
                    eQ13.append(q13)
                    eM2.append(m2)
                    eM3.append(m3)
                    eTskin.append(tskin)
                    eTlat.append(tlat)
                    eTlat2.append(tlat2)
            except:
                print ('Exception reading EmbeddedBeam in phase' + phase.Name.value)
        
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID,ElementID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N(kN),Q12(kN),Q13(kN),M2(kNm),M3(kNm),Tskin(kN/m),Tlat(kN/m),Tlat2(kN/m)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2):
                row = []        
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n)
                row.append(q12)
                row.append(q13)
                row.append(m2)
                row.append(m3)
                row.append(tskin)
                row.append(tlat)
                row.append(tlat2)
                self.insertValues(row)
                
        print('getEmbeddedBeamResults Done')
        
    def getInterfaceResults(self,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
        # file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_Interface.html
        
        self.setPhaseOrder(sphaseOrder,
           sphaseStart,
           sphaseEnd)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResults' 
        print('FileOut=', fileOut)
        
        # initialize data for lists
        iPhaseName = []
        iPhaseIdent = []

        iY = []
        iX = []
        iZ = []
        
        iMat = []
               
        iUx = []
        iUy = []
        iUz = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUz = []
        iPUt = []

        iU1 = []
        iU2 = []
        iU3 = []
        
        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []
        
        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            try:
                interX = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.X, 'node')
                interY = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Y, 'node')
                interZ = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Z, 'node')
                
                interMat = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.MaterialID, 'node')
                               
                interUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Ux, 'node')
                interUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Uy, 'node')
                interUz = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Uz, 'node')
                interUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.Utot, 'node')

                interPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUx, 'node')
                interPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUy, 'node')
                interPUz = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUz, 'node')
                interPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PUtot, 'node')

                interU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.U1, 'node')
                interU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.U2, 'node')
                interU3 = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.U3, 'node')
                
                interEffNormalStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceEffectiveNormalStress, 'node')
                interTotNormalStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceTotalNormalStress, 'node')
                interShearStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceShearStress, 'node')
                interRelShearStress = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.InterfaceRelativeShearStress, 'node')

                interPExcess = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PExcess, 'node')
                interPActive = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PActive, 'node')
                interPSteady = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PSteady, 'node')
                interPWater = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.PWater, 'node')
                
                interSuction = self.g_o.getresults(phase,self.g_o.ResultTypes.Interface.Suction, 'node')
                interEffSuction = self.g_o.getresults(phase, self.g_o.ResultTypes.Interface.EffSuction, 'node')

                for x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(
                        interX, interY, interZ, interMat, 
                        interUx, interUy, interUz, interUt, 
                        interPUx, interPUy, interPUz, interPUt, 
                        interU1, interU2, interU3,
                        interEffNormalStress, interTotNormalStress, interShearStress, interRelShearStress,
                        interPExcess, interPActive, interPSteady, interPWater, 
                        interSuction,  interEffSuction):
                    # add filters in here if necessary
                    
                    iPhaseName.append(phase.Name.value)
                    iPhaseIdent.append(phase.Identification.value)
                    
                    iX.append(x)
                    iY.append(y)
                    iZ.append(z)
                    
                    iMat.append(mat)
                                        
                    iUx.append(ux)
                    iUy.append(uy)
                    iUz.append(uz)
                    iUt.append(ut)
                    
                    iPUx.append(pux)
                    iPUy.append(puy)
                    iPUz.append(puz)
                    iPUt.append(put)
                    
                    iU1.append(u1)
                    iU2.append(u2)
                    iU3.append(u3)
                     
                    iEffNormalStress.append(ens)
                    iTotNormalStress.append(tns)
                    iShearStress.append(ss)
                    iRelShearStress.append(rss)
                    iPExcess.append(pe)
                    iPActive.append(pa)
                    iPSteady.append(pst)
                    iPWater.append(pw)
                    iSuction.append(su)
                    iEffSuction.append(esu)
            
            except Exception as e:
                msg = '...exception reading interface results ' + phase.Identification.value
                print (msg)
                self.logger.error(msg + str(e))
                    
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                in zip(iPhaseName, iPhaseIdent, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu)
                for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu 
                in zip(iPhaseName, iPhaseIdent, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(ens)
                row.append(tns)
                row.append(ss)
                row.append(rss)
                row.append(pe)
                row.append(pa)
                row.append(pst)
                row.append(pw)
                row.append(su)
                row.append(esu)
                self.insertValues(row)
                
        print('getInterfaceResults Done') 
        
    def getInterfaceResultsByPoints(self,
                    filePoints=None,
                    fileOut=None,
                    tableOut=None,
                    sphaseOrder=None,
                    sphaseStart=None,
                    sphaseEnd=None
                    ):
                        
        if self.phaseOrder is None:
            self.setPhaseOrder(sphaseOrder,
                               sphaseStart,
                               sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1


        if not filePoints is None:
            self.loadXYZNodeList(filePoints)


        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getInterfaceResultsByPoints'  

        print('FileOut=', fileOut)

        # initialize data for lists
        iPhaseName = []
        iPhaseIdent = []

        iLocName = []

        iY = []
        iX = []
        iZ = []

        iMat = []
               
        iUx = []
        iUy = []
        iUz = []
        iUt = []

        iPUx = []
        iPUy = []
        iPUz = []
        iPUt = []

        iU1 = []
        iU2 = []
        iU3 = []

        iEffNormalStress = []
        iTotNormalStress = []
        iShearStress = []
        iRelShearStress = []

        iPExcess = []
        iPActive = []
        iPSteady = []
        iPWater = []

        iSuction = []
        iEffSuction = []

        for phase in self.phaseOrder:

            print('Getting Interface results for Phase ', phase.Name.value)
            
            for pt in self.NodeList:
            
                try:
                    x = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.X, (pt.x, pt.y, pt.z))
                    y = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Y, (pt.x, pt.y, pt.z))
                    z = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Z, (pt.x, pt.y, pt.z))
                    mat = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.MaterialID,  (pt.x, pt.y, pt.z))
                                   
                    ux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Ux, (pt.x, pt.y, pt.z))
                    uy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Uy, (pt.x, pt.y, pt.z))
                    uz = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Uz, (pt.x, pt.y, pt.z))
                    ut = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Utot, (pt.x, pt.y, pt.z))

                    pux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PUx, (pt.x, pt.y, pt.z))
                    puy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PUy, (pt.x, pt.y, pt.z))
                    puz = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PUz, (pt.x, pt.y, pt.z))
                    put = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PUtot, (pt.x, pt.y, pt.z))

                    u1 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.U1, (pt.x, pt.y, pt.z))
                    u2 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.U2, (pt.x, pt.y, pt.z))
                    u3 = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.U3, (pt.x, pt.y, pt.z))
                    
                    ens = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.InterfaceEffectiveNormalStress, (pt.x, pt.y, pt.z))
                    tns = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.InterfaceTotalNormalStress, (pt.x, pt.y, pt.z))
                    ss = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.InterfaceShearStress, (pt.x, pt.y, pt.z))
                    rss = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.InterfaceRelativeShearStress, (pt.x, pt.y, pt.z))

                    pe = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PExcess, (pt.x, pt.y, pt.z))
                    pa = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PActive, (pt.x, pt.y, pt.z))
                    pst = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PSteady, (pt.x, pt.y, pt.z))
                    pw = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.PWater, (pt.x, pt.y, pt.z))
                    
                    su = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.Suction, (pt.x, pt.y, pt.z))
                    esu = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Interface.EffSuction, (pt.x, pt.y, pt.z))
                    
                    if ux == 'not found':
                        print('results for ', phase.Name.value, pt.name, pt.x, pt.y, pt.z ,' not found')
                    if ux != 'not found':
                        print('results for ', phase.Name.value, pt.name, pt.x, pt.y, pt.z ,' retrieved')
                        # add filters in here if necessary
                        iPhaseName.append(phase.Name.value)
                        iPhaseIdent.append(phase.Identification.value)
                        
                        iX.append(x)
                        iY.append(y)
                        iZ.append(z)
                        
                        iMat.append(mat)
                        iLocName.append (pt.name)
                        
                        iUx.append(ux)
                        iUy.append(uy)
                        iUz.append(uz)
                        iUt.append(ut)
                        
                        iPUx.append(pux)
                        iPUy.append(puy)
                        iPUz.append(puz)
                        iPUt.append(put)
                        
                        iU1.append(u1)
                        iU2.append(u2)
                        iU3.append(u3)
                         
                        iEffNormalStress.append(ens)
                        iTotNormalStress.append(tns)
                        iShearStress.append(ss)
                        iRelShearStress.append(rss)
                        iPExcess.append(pe)
                        iPActive.append(pa)
                        iPSteady.append(pst)
                        iPWater.append(pw)
                        iSuction.append(su)
                        iEffSuction.append(esu)
                        
                except:
                    print ('Exception reading Interface results in phase' + phase.Name.value)

        columns ='Phase,PhaseIdent,LocName,X(m),Y(m),Z(m),MaterialID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),Eff NormalStress (kPa),Tot Normal Stress (kPa),Shear Stress (kPa),Rel Shear Stress (kPa),Excess Porewater (kPa),Active Porewater (kPa),Steady Porewater (kPa),Suction Porewater (kPa),Porewater (kPa),Effective Suction Porewater (kPa)'
        formats = '{},{},{},{:2f},{:2f},{:2f},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, loc, float(x), float(y), float(z), float(mat), float(ux), float(uy), float(uz), float(ut), float(pux), float(puy), float(puz), float(put), float(u1), float(u2),float(u3), float(ens), float(tns), float(ss), float(rss), float(pe), float(pa), float(pst), float(pw), float(su), float(esu))
                for pname, pident, loc, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
            return columns + rows
        
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            
            #~ print(iLocName)
            #~ print(iPhaseName)
            #~ print(iPhaseIdent)
            #~ print(iX)
            #~ print(iY)
            #~ print(iZ)
            #~ print(iMat)
            
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, loc, float(x), float(y), float(z), float(mat), float(ux), float(uy), float(uz), float(ut), float(pux), float(puy), float(puz), float(put), float(u1), float(u2),float(u3), float(ens), float(tns), float(ss), float(rss), float(pe), float(pa), float(pst), float(pw), float(su), float(esu))
                for pname, pident, loc, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction)])
       
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, loc, x, y, z, mat, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, ens, tns, ss, rss, pe, pa, pst, pw, su, esu in zip(iPhaseName, iPhaseIdent, iLocName, iX, iY, iZ, iMat, iUx, iUy, iUz, iUt, iPUx, iPUy, iPUz, iPUt, iU1, iU2, iU3, iEffNormalStress, iTotNormalStress, iShearStress, iRelShearStress, iPExcess, iPActive, iPSteady, iPWater, iSuction, iEffSuction):
                row = []
                row.append(pname)
                row.append(pident)
                row.append(loc)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(ens)
                row.append(tns)
                row.append(ss)
                row.append(rss)
                row.append(pe)
                row.append(pa)
                row.append(pst)
                row.append(pw)
                row.append(su)
                row.append(esu)
                self.insertValues(row)

        print('getInterfaceResultsByPoints Done')     
class Plaxis3dResultsConnect (Plaxis3dResults2018): 
    def __init__(self,
                server=None, host=None, port=None, password=None
                 ):
        super(Plaxis3dResultsConnect, self).__init__(server, host, port, password)
    def version (self):
        return "Plaxis3dConnect"
    def getEmbeddedBeamResults(self,
                                  fileOut=None,
                                  tableOut=None,
                                  sphaseOrder=None,
                                  sphaseStart=None,
                                  sphaseEnd=None,
                                  ):
# file:///C:/Program%20Files/Plaxis/PLAXIS%203D/manuals/english/output_objects/objects_EmbeddedBeam.html
        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getEmbeddedBeamResults'  
        
        print('FileOut=', fileOut)

        # init data for lists
        PhaseName = []
        PhaseIdent = []
           
        eY = []
        eX = []
        eZ = []
        
        eMat = []
        eEl = []
        
        eUx = []
        eUy = []
        eUz = []
        eUt = []

        ePUx = []
        ePUy = []
        ePUz = []
        ePUt = []

        eU1 = []
        eU2 = []
        eU3 = []
        
        eN = []
        eQ12 = []
        eQ13 = []
        eM2 = []
        eM3 = []

        eTskin = []
        eTlat = []
        eTlat2 = []
        eFfoot = []
        
        for phase in self.phaseOrder:

            print('Getting EmbeddedBeam results for Phase ',  phase.Name.value)
            
            try:
                embeamX = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.X, 'node')
                embeamY = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Y, 'node')
                embeamZ = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Z, 'node')
                #print('Retrieved U')
                ebeamMat = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.MaterialID, 'node')
                ebeamEl = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.ElementID, 'node')
                                
                embeamUx = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Ux, 'node')
                embeamUy = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Uy, 'node')
                embeamUz = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Uz, 'node')
                embeamUt = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Utot, 'node')
                #print('Retrieved U')
                embeamPUx = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.PUx, 'node')
                embeamPUy = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.PUy, 'node')
                embeamPUz = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.PUz, 'node')
                embeamPUt = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.PUtot, 'node')
                #print('Retrieved dU')
                embeamU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.U1, 'node')
                embeamU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.U2, 'node')
                embeamU3 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.U3, 'node')
                #print('Retrieved U1-U3')
                embeamN = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.N, 'node')
                embeamQ12 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Q12, 'node')
                embeamQ13 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Q13, 'node')
                embeamM2 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.M2, 'node')
                embeamM3 = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.M3, 'node')
                #print('Retrieved N')
                embeamTskin = self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Tskin, 'node')
                embeamTlat= self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Tlat, 'node')
                embeamTlat2= self.g_o.getresults(phase, self.g_o.ResultTypes.EmbeddedBeam.Tlat2, 'node')
                #embeamFfoot= self.g_o.getresults(phase, self.g_o.ResultsTypes.EmbeddedBeam.Tlat2, 'node')
                
                print('Retrieved EmbeddedBeam results for ', phase.Name.value)
                
                for x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(
                        embeamX, embeamY, embeamZ, ebeamMat, ebeamEl, embeamUx, embeamUy, embeamUz, embeamUt, embeamPUx, embeamPUy,  embeamPUz, embeamPUt, embeamU1, embeamU2, embeamU3, embeamN, embeamQ12, embeamQ13, embeamM2, embeamM3, embeamTskin, embeamTlat, embeamTlat2):
                    # add filters in here if necessary
                    PhaseName.append(phase.Name.value)
                    PhaseIdent.append(phase.Identification.value)
                    eX.append(x)
                    eY.append(y)
                    eZ.append(z)
                    eMat.append(mat)
                    eEl.append(el)
                    eUx.append(ux)
                    eUy.append(uy)
                    eUz.append(uz)
                    eUt.append(ut)
                    ePUx.append(pux)
                    ePUy.append(puy)
                    ePUz.append(puz)
                    ePUt.append(put)
                    eU1.append(u1)
                    eU2.append(u2)
                    eU3.append(u3)
                    eN.append(n)  
                    eQ12.append(q12)
                    eQ13.append(q13)
                    eM2.append(m2)
                    eM3.append(m3)
                    eTskin.append(tskin)
                    eTlat.append(tlat)
                    eTlat2.append(tlat2)
            except:
                print ('Exception reading EmbeddedBeam in phase' + phase.Name.value)
        
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID,ElementID,Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N(kN),Q12(kN),Q13(kN),M2(kNm),M3(kNm),Tskin(kN/m),Tlat(kN/m),Tlat2(kN/m)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)])
            return columns + rows

        if (fileOut == None and tableOut == None):
            file = StringIO()
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            file.write(columns)
            file.write(''.join([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)]))
            contents = file.getvalue()                               
            file.close()
            return contents

        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n, q12, q13, m2, m3, tskin, tlat, tlat2 in zip(PhaseName, PhaseIdent, eX, eY, eZ, eMat, eEl, eUx, eUy, eUz, eUt, ePUx, ePUy, ePUz, ePUt, eU1, eU2, eU3, eN, eQ12, eQ13, eM2, eM3, eTskin, eTlat, eTlat2):
                row = []        
                row.append(pname)
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n)
                row.append(q12)
                row.append(q13)
                row.append(m2)
                row.append(m3)
                row.append(tskin)
                row.append(tlat)
                row.append(tlat2)
                self.insertValues(row)
                
        print('getEmbeddedBeamResults Done')  
    
    def getPlateResults(self,
                        fileOut=None,
                        tableOut=None,
                        sphaseOrder=None,
                        sphaseStart=None,
                        sphaseEnd=None
                        ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)

        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getPlateResults'  
        print('FileOut=', fileOut)

        # initialise data for lists
        pPhaseName = []
        pPhaseIdent = []
           
        pY = []
        pX = []
        pZ = []
        
        pMat = []
        pEl = []
               
        pUx = []
        pUy = []
        pUz = []
        pUt = []

        pPUx = []
        pPUy = []
        pPUz = []
        pPUt = []

        pU1 = []
        pU2 = []
        pU3 = []
        
        pM11 = []
        pM22 = []
        pM12 = []
        
        pQ12 = []
        pQ23 = [] 
        pQ13 = []
        
        pN1 = []
        pN2 = []



        for phase in self.phaseOrder:
            print('Getting Plate results for Phase ', phase.Name.value, phase.Identification.value)
            
            try: 
                plateX = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.X, 'node')
                plateY = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Y, 'node')
                plateZ = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Z, 'node')
                
                plateMat = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.MaterialID, 'node')
                plateEl = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.ElementID, 'node')
                                
                plateUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Ux, 'node')
                plateUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Uy, 'node')
                plateUz = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Uz, 'node')
                plateUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Utot, 'node')

                platePUx = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUx, 'node')
                platePUy = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUy, 'node')
                platePUz = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUz, 'node')
                platePUt = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.PUtot, 'node')

                plateU1 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.U1, 'node')
                plateU2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.U2, 'node')
                plateU3 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.U3, 'node')
                
                plateN1 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.N11, 'node')
                plateN2 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.N22, 'node')                
                plateQ12 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Q12, 'node')
                plateQ23 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Q23, 'node')
                plateQ13 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.Q13, 'node')
                plateM11 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.M11, 'node')
                plateM22 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.M22, 'node')
                plateM12 = self.g_o.getresults(phase, self.g_o.ResultTypes.Plate.M12, 'node')
                
                for x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(
                        plateX, plateY, plateZ, plateMat, plateEl, plateUx, plateUy, plateUz, plateUt, platePUx, platePUy, platePUz, platePUt, plateU1, plateU2, plateU3, plateN1, plateN2, plateQ12, plateQ23, plateQ13, plateM11, plateM22, plateM12):
                    # add filters in here if necessary
                    pPhaseName.append(phase.Name.value)
                    pPhaseIdent.append(phase.Identification.value)
                    
                    pX.append(x)
                    pY.append(y)
                    pZ.append(z)
                    pMat.append(mat)
                    pEl.append (el)
                   
                    pUx.append(ux)
                    pUy.append(uy)
                    pUz.append(uz)
                    pUt.append(ut)
                    
                    pPUx.append(pux)
                    pPUy.append(puy)
                    pPUz.append(puz)
                    pPUt.append(put)
                   
                    pU1.append(u1)
                    pU2.append(u2)
                    pU3.append(u3)
                    
                    pN1.append(n1)
                    pN2.append(n2)
                    pQ12.append(q12)
                    pQ23.append(q23)
                    pQ13.append(q13)
                    pM11.append(m11)                    
                    pM22.append(m22)                  
                    pM12.append(m12) 
            except Exception as e:
                print ('Exception reading Plate in phase' + phase.Name.value)
                self.logger.error('...exception reading Plate results  '+ str(e))
        columns ='Phase,PhaseIdent,X(m),Y(m),Z(m),MaterialID, ElementID, Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUt(m),U1(m),U2(m),U3(m),N1(kN/m),N2(kN/m),Q12(kN/m),Q23(kN/m),Q13(kN/m),M11(kNm/m),M22(kNm/m),M12(kNm/m)'
        formats = '{},{},{:2f},{:2f},{:2f},{:0},{:0},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f},{:2f}'
        
        if (fileOut == None and tableOut == None):
            print('Outputting to string....')
            columns += '\n'
            formats += '\n'
            rows = ''.join([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pEl, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
            return columns + rows

        if (fileOut != None and tableOut == None):
            columns += '\n'
            formats += '\n'
            print('Outputting to file ', fileOut, '....')
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12)
                                 for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pEl, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12)])
        
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            print (self.columns)
            print (self.formats)
            print (self.types)
            for pname, pident, x, y, z, mat, el, ux, uy, uz, ut, pux, puy, puz, put, u1, u2, u3, n1, n2, q12, q23, q13, m11, m22, m12 in zip(pPhaseName, pPhaseIdent, pX, pY, pZ, pMat, pEl, pUx, pUy, pUz, pUt, pPUx, pPUy, pPUz, pPUt, pU1, pU2, pU3, pN1, pN2, pQ12, pQ23, pQ13,pM11, pM22, pM12):
                row= []
                row.append(pname) 
                row.append(pident)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(mat)
                row.append(el)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(ut)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(put)
                row.append(u1)
                row.append(u2)
                row.append(u3)
                row.append(n1)
                row.append(n2)
                row.append(q12)
                row.append(q23)
                row.append(q13)
                row.append(m11)
                row.append(m22)
                row.append(m12)
                self.insertValues(row)
        
        print('getPlateResults Done')
      
    def getSoilResultsByPoints_Displacements(self,
                               filePoints=None,
                               fileOut=None,
                               tableOut=None,
                               sphaseOrder=None,
                               sphaseStart=None,
                               sphaseEnd=None,
                               ):

        self.setPhaseOrder(sphaseOrder,
                           sphaseStart,
                           sphaseEnd)
        
        if not filePoints is None:
            self.loadXYZNodeList(filePoints)
        
        if self.phaseOrder is None:
            print('No phases found for results')
            return -1
        
        if (self.IsDbFile(fileOut) and not tableOut):
            tableOut = 'getSoilResultsByPoints_Displacements'  
            
        phaseName = []
        phaseIdent = []
        
        locName = []
        locY = []
        locX = []
        locZ = []
       
        Uyy = []
        Uxx = []
        Uzz = []
        Utot = []
        
        PUyy = []
        PUxx = []
        PUzz = []
        PUtot = []
        
        Epsyy = []
        Epsxx = []
        Epszz = []

            
        for phase in self.phaseOrder:
            print(phase.Name.value)
    
            for pt in self.NodeList:
            
                ux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Ux, (pt.x, pt.y, pt.z))
                uy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Uy, (pt.x, pt.y, pt.z))
                uz = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Uz, (pt.x, pt.y, pt.z))
                utot = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Utot, (pt.x, pt.y, pt.z))
                 
                pux = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUx, (pt.x, pt.y, pt.z))
                puy = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUy, (pt.x, pt.y, pt.z))
                puz = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUz, (pt.x, pt.y, pt.z))
                putot = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.PUtot, (pt.x, pt.y, pt.z)) 
                
                ex = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Epsxx, (pt.x, pt.y, pt.z))
                ey = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Epsyy, (pt.x, pt.y, pt.z))
                ez = self.g_o.getsingleresult(phase, self.g_o.ResultTypes.Soil.Epszz, (pt.x, pt.y, pt.z))
                
                if ux != 'not found':
                    print('results for ', phase.Name.value, pt.x, pt.y, pt.z ,' retrieved')
                
                    phaseName.append(phase.Name.value)
                    phaseIdent.append(phase.Identification.value)
                
                    locName.append (pt.name)
                    locX.append (pt.x)
                    locY.append (pt.y)
                    locZ.append (pt.z)
                                     
                    Uxx.append (ux)
                    Uyy.append (uy)
                    Uzz.append (uz)
                    Utot.append (utot)
                
                    PUxx.append (pux)
                    PUyy.append (puy)
                    PUzz.append (puz)
                    PUtot.append (putot)
                
                    Epsxx.append (ex)
                    Epsyy.append (ey)
                    Epszz.append (ez)
              
                
        columns='Phase,PhaseIdent,locName,locX(m),locY(m),locZ(m),Ux(m),Uy(m),Uz(m),Utot(m),PUx(m),PUy(m),PUz(m),PUtot(m),Epsxx,Epsyy,Epszz'
        formats='{},{},{},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:f}'                
        if (fileOut != None and tableOut == None):
            print('Outputting to file ', fileOut, '....')
            columns += '\n'
            formats += '\n'
            with open(fileOut, "w") as file:
                file.writelines([columns])
                file.writelines([formats.format(pName, pIdent,locname, float(x), float(y), float(z), float(ux), float(uy), float(uz), float(utot), float(pux), float(puy), float(puz), float(putot), float(ex), float(ey), float(ez))
                for pName, pIdent, locname, x, y, z, ux, uy, uz, utot, pux, puy, puz, putot, ex, ey, ez in zip(phaseName, phaseIdent, locName, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, Epsxx, Epsyy, Epszz)])
        if (fileOut != None and tableOut != None):
            print('Outputting to database ', fileOut, '....')
            self.getConnected (fileOut)
            self.createTable(tableOut, columns, formats)
            for pName, pIdent, locname, x, y, z, ux, uy, uz, utot, pux, puy, puz, putot, ex, ey, ez in zip(phaseName, phaseIdent, locName, locX, locY, locZ, Uxx, Uyy, Uzz, Utot, PUxx, PUyy, PUzz, PUtot, Epsxx, Epsyy, Epszz):
                row = []
                row.append(pName)
                row.append(pIdent)
                row.append(locname)
                row.append(x)
                row.append(y)
                row.append(z)
                row.append(ux)
                row.append(uy)
                row.append(uz)
                row.append(utot)
                row.append(pux)
                row.append(puy)
                row.append(puz)
                row.append(putot)
                row.append(ex)
                row.append(ey)
                row.append(ez)
                self.insertValues(row)
                