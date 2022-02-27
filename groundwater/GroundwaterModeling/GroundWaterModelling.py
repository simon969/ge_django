
import numpy as np
import math
import datetime as dt

 # http://www.bgs.ac.uk/research/environmentalModelling/Modellingflowtoboreholes.html
# http://www.oomodels.info/pmwiki/pmwiki.php/Main/OOModelsHome

#https://stackoverflow.com/questions/10791588/getting-container-parent-object-from-within-python
#===============================================================================================
#
#
#===============================================================================================
#
#
#===============================================================================================
#
#
#===============================================================================================

class DewateringSite:
    def __init__(self, Name):
        self.Name = Name 
        self.GroundModel = GroundModel (self.Name + ': Ground Model') 
        self.Wells = []
    def addStrata(self, Name, FromLevel, ToLevel, DensityDry, DensitySub, WaterLevel, FactorEModPo):
        self.GroundModel.addStrata(Name, FromLevel, ToLevel, DensityDry, DensitySub, WaterLevel, FactorEModPo)

    def addWell (self, Name, x, y, PumpingRate, Transmissivity, PumpingDuration, StorageCoefficent):
        w1 = Well(Name, x, y, PumpingRate, Transmissivity, PumpingDuration, StorageCoefficent, self.GroundModel)
        self.Wells.append(w1)

    def addWellStrata(self, StrataName, WellName, Efficiency):
        for s in self.GroundModel.Strata:
            if (s.Name == StrataName):
                for w in self.Wells:
                    if (w.Name == WellName):
                        w.addStrata (s.Name, Efficiency)

    def getDrawdown(self, StrataName, x, y):
        d = 0.000
        for w in self.Wells:
            if (w.getStrataId(StrataName)!=-1):
                w.setDistance (x,y)
                d = d + w.getDrawdown()
        #   print ("DewateringSite.getDrawdown d: %f"%(d))
        return d
   
    def setSettlementLevel (self, z):
        for w in self.Wells:
            w.calcSettlement (z)
 
    def getSettlement(self, x, y): 
        s = 0.0000
        
        for w in self.Wells:
            w.setDistance (x, y)
            s = s + w.getSettlement()
          
        # print ("DewateringSite.getSettlement %f, %f, %f"%(x,y,s))
        return s

    def calcWellProfiles(self, count):
        if (count is None):
            count = 80
        for w in self.Wells:
            w.calcDrawdown (count, 0.5, 2)
            w.Print()
    
    def calcGroundModel(self):
        self.GroundModel.calcInitialStress()
        self.GroundModel.calcStress()
        self.GroundModel.Print()    






class GroundModel:
    def __init__(self, Name):
        self.Name = Name
        self.Strata = []

    def addStrata(self, Name, FromLevel, ToLevel, DensityDry, DensitySub, WaterLevel, FactorEModPo):
        s1 = Strata (Name, FromLevel, ToLevel, DensityDry, DensitySub, WaterLevel, FactorEModPo)
        self.Strata.append (s1)	
    
    def getStrata(self, StrataName):
        for s in self.Strata:
            if (s.Name == StrataName):
                return s
                
    def setStrataWaterLevel (self, StrataName, WaterLevel):
        for s in self.Strata:
            if (s.Name == StrataName):
                s.WaterLevel =  WaterLevel
    
    def setStrataDrawdown(self, StrataName, Drawdown):
        for s in self.Strata:
            if (s.Name == StrataName):
                s.WaterLevel =  s.InitialWaterLevel - float(Drawdown)
         #       print ("%s, %.2f, %.2f, %.2f" % (StrataName, s.WaterLevel, s.InitialWaterLevel, Drawdown))
      
    def calcStress(self):
        s1 = 0.00
        for s in self.Strata:
            s1 = s.calcStress(s1)
    #    print("Groundmodel %s Total Stresses and Stiffnesses calculated" % (self.Name)) 
    def calcInitialStress(self):
        s1 = 0.00
        for s in self.Strata:
            s1 = s.calcInitialStress(s1)
            
    def calcEModulus(self, StressState):
        for s in self.Strata:
            if (StressState == "Initial"):
                s.calcInitialStressEModulus()
            else:
                s.calcEModulus()
    
    def Print(self):
        print("Ground Model Name         %s" % self.Name)
        for s in self.Strata:
            s.Print()
    def Print_tabular(self):
        print ("Strata  Level Level  Thick Density Density FactorEmodPo Initial  Initial Inital Initial Initial                                     Change           Water")
        print ("Name    Top   Bottom       Dry     Sub                  Water    Top Sz  Int Sz Bot Sz  Avg Sz  Water Top Sz  Int Sz Bot Sz  Avg Sz Avg Sz Emodulus  State")
        for s in self.Strata:
            s.Print_tabular()




class Strata:
    
    
    
    def __init__(self, Name, LevelTop, LevelBot, DensityDry, DensitySub, WaterLevel, FactorEModPo):
        self.Name = Name
        self.LevelTop = float(LevelTop)
        self.LevelBot = float(LevelBot)
        self.DensityDry = float(DensityDry)
        self.DensitySub = float(DensitySub)
        self.DensityWater = 10.0
        
        self.InitialWaterLevel = float(WaterLevel)
        self.WaterLevel = float(WaterLevel)
        self.FactorEModPo = FactorEModPo
        
        self.TotalStressTop = 0.0
        self.TotalStressInt = 0.0
        self.TotalStressBot = 0.0
        self.TotalStressAvg = 0.0
        self.PWPAvg = 0.0
        
        self.InitialTotalStressTop = 0.0
        self.InitialTotalStressInt = 0.0
        self.InitialTotalStressBot = 0.0
        self.InitialTotalStressAvg = 0.0
        self.InitialPWPAvg = 0.0
        
        self.ChangeEffectiveStressAvg = 0.0
        self.EModulus = 0.0
        self.Thickness = self.LevelTop - self.LevelBot
        
        self.getWaterState()
        
    def getWaterState (self):   
        if (self.WaterLevel > self.LevelTop):
            self.WaterState = "Confined"
        else:
            self.WaterState ="UnConfined"
        return self.WaterState
            
    def calcInitialStress (self, TotalStressTop):

        self.InitialTotalStressTop = TotalStressTop	
        
        if (self.InitialWaterLevel >= self.LevelTop):
            self.InitialTotalStressBot = TotalStressTop + self.Thickness * self.DensitySub
            self.InitialPWPAvg = self.DensityWater * (self.InitialWaterLevel - (self.LevelTop + self.LevelBot) / 2.0)
        
        if (self.InitialWaterLevel <= self.LevelBot):
            self.InitialTotalStressBot = TotalStressTop + self.Thickness * self.DensityDry
            self.InitialPWPAvg = 0.0
        
        if (self.InitialWaterLevel > self.LevelBot and self.InitialWaterLevel < self.LevelTop):
            Thickness_Dry = self.LevelTop - self.InitialWaterLevel  
            Thickness_Sub = self.InitialWaterLevel - self.LevelBot
            self.InitialTotalStressInt = TotalStressTop + Thickness_Dry * self.DensityDry
            self.InitialTotalStressBot = TotalStressTop + Thickness_Dry * self.DensityDry + Thickness_Sub * self.DensitySub
            s1 = Thickness_Dry * (self.InitialTotalStressInt + self.InitialTotalStressTop) / 2.0
            s2 = Thickness_Sub * (self.InitialTotalStressInt + self.InitialTotalStressBot) / 2.0
            self.InitialTotalStressAvg = (s1 + s2) / self.Thickness
            self.InitialPWPAvg = self.DensityWater * Thickness_Sub / self.Thickness
        else:
            self.InitialTotalStressAvg  = (self.InitialTotalStressTop + self.InitialTotalStressBot) / 2.0
                    
        return self.InitialTotalStressBot
        
    def calcStress (self, TotalStressTop):
        
        self.TotalStressTop = TotalStressTop
        
        if (self.WaterLevel >= self.LevelTop):
            self.TotalStressBot = TotalStressTop + self.Thickness * self.DensitySub 
            self.PWPAvg = self.DensityWater * (self.WaterLevel - (self.LevelTop + self.LevelBot) / 2.0)
            
        if (self.WaterLevel <= self.LevelBot):
            self.TotalStressBot = TotalStressTop + self.Thickness * self.DensityDry
            self.PWPAvg = 0.0
            
        if (self.WaterLevel > self.LevelBot and self.WaterLevel < self.LevelTop):
            Thickness_Dry = self.LevelTop - self.WaterLevel  
            Thickness_Sub = self.WaterLevel - self.LevelBot
            self.TotalStressInt = TotalStressTop + Thickness_Dry * self.DensityDry
            self.TotalStressBot = TotalStressTop + Thickness_Sub * self.DensitySub + Thickness_Dry * self.DensityDry
            s1 = Thickness_Dry * (self.TotalStressInt + self.TotalStressTop) / 2.0
            s2 = Thickness_Sub * (self.TotalStressInt + self.TotalStressBot) / 2.0
            self.TotalStressAvg = (s1 + s2) / self.Thickness
            self.PWPAvg = self.DensityWater * Thickness_Sub / self.Thickness
        else:
            self.TotalStressAvg = (self.TotalStressTop + self.TotalStressBot) / 2.0
        
        self.ChangeEffectiveStressAvg = (self.TotalStressAvg - self.PWPAvg) - (self.InitialTotalStressAvg - self.InitialPWPAvg)      
        
        return self.TotalStressBot
    def calcInitialStressEModulus(self):
        self.EModulus = self.FactorEModPo * self.InitialTotalStressAvg 
    #    print("Strata %s stiffness calculated (%s)" % (self.Name, self.EModulus)) 
    def calcEModulus(self):
        self.EModulus = self.FactorEModPo * self.TotalStressAvg 
    #    print("Strata %s stiffness calculated (%s)" % (self.Name, self.EModulus)) 
    def Print(self):
        print("===================================================")
        print("Strata Name              %s" % self.Name)
        print("Level Top                %s" % self.LevelTop)
        print("Level Bot                %s" % self.LevelBot)
        print("Thickness                %s" % self.Thickness)
        print("Density Dry              %s" % self.DensityDry)
        print("Density Sub              %s" % self.DensitySub)
        print("FactorEModPo             %s" % self.FactorEModPo)
        print("Inital Water Level       %s" % self.InitialWaterLevel)
        print("Initial Total Stress Top %s" % self.InitialTotalStressTop)
        print("Initial Total Stress Bot %s" % self.InitialTotalStressBot)
        print("Initial Total Stress Int %s" % self.InitialTotalStressInt)
        print("Initial Total Stress Avg %s" % self.InitialTotalStressAvg)
        print("Initial PWP Avg          %s" % self.InitialPWPAvg)
        print("----------------------------")
        print("Water Level              %s" % self.WaterLevel)
        print("Total Stress Top         %s" % self.TotalStressTop)
        print("Total Stress Bot         %s" % self.TotalStressBot)
        print("Total Stress Int         %s" % self.TotalStressInt)
        print("Total Stress Avg         %s" % self.TotalStressAvg)
        print("PWP Avg                  %s" % self.PWPAvg)
        print("Change Effective         %s" % self.ChangeEffectiveStressAvg)
        print("EModulus                 %s" % self.EModulus)
        print("WaterState               %s" % self.WaterState)
        print("===================================================")
    def Print_tabular(self):
    #    print ("Strata  Level Level  Thick Density Density FactorEmodPo Initial  Initial Inital Initial Initial Inital                                              Change           Water")
    #    print ("Name    Top   Bottom       Dry     Sub                  Water    Top Sz  Int Sz Bot Sz  Avg Sz  PWP Avg Water Top Sz  Int Sz Bot Sz  Avg Sz PWP Avg Avg Sz Emodulus  State")
        print ("%5s  %.2f  %.2f  %.2f %.2f  %.2f    %.1f         %.2f     %.2f    %.2f   %.2f    %.2f    %.2f    %.2f   %.2f    %.2f  %.2f    %.2f   %.2f    %.2f   %.1f      %s   "%(self.Name[0:5],self.LevelTop,self.LevelBot,self.Thickness,self.DensityDry,self.DensitySub,self.FactorEModPo,self.InitialWaterLevel, self.InitialTotalStressTop, self.InitialTotalStressInt,  self.InitialTotalStressBot, self.InitialTotalStressAvg, self.InitialPWPAvg,self.WaterLevel, self.TotalStressTop, self.TotalStressInt,  self.TotalStressBot, self.TotalStressAvg, self.PWPAvg,self.ChangeEffectiveStressAvg,self.EModulus, self.WaterState))
class WellStrata():
    def __init__(self, Name, Efficiency):
        self.Name = Name
        self.Efficiency = Efficiency
        
class Well():
    def __init__(self, Name, x, y, PumpingRate, Transmissivity, PumpingDuration, StorageCoefficient, GroundModel):
        self.Name = Name
        self.x = x
        self.y = y
        self.PumpingRate = PumpingRate
        self.Transmissivity = Transmissivity
        self.PumpingDuration = PumpingDuration
        self.StorageCoefficient = StorageCoefficient
        self.WellStrata = []
        self.distance = 0.0
        self.GroundModel = GroundModel
        
        self.confinedF1 = 2.3 * self.PumpingRate / (4 * math.pi  * self.Transmissivity)
        
        self.DensityWater = 10.0
        
        self.FactorSettlement = -1000.0
        
        self.FactorDrawdown = -1.0
        
    def addStrata(self, Name, Efficiency):
        
        ws = WellStrata(Name, Efficiency)
        
        self.WellStrata.append (ws)
    
    def calcDrawdownConfinedJacobsEquation(self, r):
        d = self.confinedF1 * math.log10((2.25 * self.Transmissivity * self.PumpingDuration) / (r**2*self.StorageCoefficient))
        return d
    
    def calcDrawdownUnconfined(self, r):
        d = self.confinedF1 * math.log10((2.25 * self.Transmissivity * self.PumpingDuration) / (r**2*self.StorageCoefficient))
        return d
    def calcDrawdown(self, count, factor_n, power_m):
        
        dim2 = len(self.WellStrata)
        
        self.radius = np.zeros( (count), dtype=float)
        self.settlement = np.zeros( (count), dtype=float)
        self.strata_drawdown = np.zeros( (dim2, count), dtype=float)
        self.strata_settlement = np.zeros( (dim2, count), dtype=float)
        self.strata_emodulus = np.zeros( (dim2, count), dtype=float)
        self.strata_changestress = np.zeros( (dim2, count), dtype=float)
         
        for i in range(0, count, 1):
            r  = ((i+1) * factor_n) ** power_m
            self.radius[i] = r 
       
        for j in range(0, dim2 ,1):
            
            strataName = self.WellStrata[j].Name
            strataEfficiency = self.WellStrata[j].Efficiency
            
            strata = self.GroundModel.getStrata(strataName) 
            
            waterState = strata.getWaterState()
            
            for i in range(0,count,1):
                
                r = self.radius[i]
                                        
                if (waterState == "Confined"):
                    d = self.calcDrawdownConfinedJacobsEquation(r) * strataEfficiency 
                else:
                    d = self.calcDrawdownUnconfined(r) * strataEfficiency 
                
                self.GroundModel.setStrataDrawdown (strataName, d)
                self.GroundModel.calcStress()
                # self.GroundModel.calcEModulus("Initial")
                self.GroundModel.calcEModulus("")
                 
                s = strata.ChangeEffectiveStressAvg / strata.EModulus * strata.Thickness 
                
                self.strata_changestress[j][i] = strata.ChangeEffectiveStressAvg 
                self.strata_emodulus[j][i] = strata.EModulus
                self.strata_drawdown[j][i] = d * self.FactorDrawdown
                self.strata_settlement[j][i] = s * self.FactorSettlement
            
            print ("Well %s drawdown and settlement profile for %s completed (%s)" % (self.Name,strataName,count))        
        
        for i in range(0, count, 1):
            for j in range (0, dim2,1):
                self.settlement[i] = self.settlement[i] + self.strata_settlement[j][i]
        
        print ("Well %s drawdown and settlement profiles combined (%s)" % (self.Name, count)) 
        
    def calcSettlement(self, z):
        print ("Calculating Settlement at Level (%s)" % (z))
        dim2 = len(self.WellStrata)
        count = len(self.radius)
        
        for i in range(0, count, 1):
            self.settlement[i] = 0
            for j in range (0, dim2,1):
                strataName = self.WellStrata[j].Name
                strata = self.GroundModel.getStrata(strataName) 
                if (z >= strata.LevelTop): 
                    s  = self.strata_settlement[j][i]
                if (z < strata.LevelTop and z > strata.LevelBot):
                    s = self.strata_settlement[j][i] * (z - strata.LevelBot) / strata.Thickness               
                self.settlement[i] = self.settlement[i] + s 
        
        print ("Well %s drawdown and settlement profiles combined (%s)" % (self.Name, count))
    def getWell(self, WellName):
        for w in self.Wells:
            if (w.Name == WellName):
                return w    
    
    def setDistance(self, x, y):
        self.distance = ((x-self.x)**2 + (y-self.y)**2)**0.5
    #    print ("Well.setDistance: well.x:%s,x:%s well.y:%s,y:%s  d:%s"%(self.x,x,self.y,y,self.distance))
 
    def getStrataId(self, StrataName):
        self.strata_id = -1
        id = 0
        for s in self.WellStrata:
            if (s.Name == StrataName):
                self.strata_id = id 
                break
            id =  id + 1    
        
        return self.strata_id
        
    def getDrawdown (self): 
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html
        dd = np.interp(self.distance, self.radius, self.strata_drawdown[self.strata_id])
    #   print ("Well.getDrawdown %s,%s"%(self.distance, dd))
        return dd
    
    def getSettlement(self):
        # https://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html
        ss = np.interp(self.distance, self.radius, self.settlement)
        # print ("Well.getSettlement %f,%f"%(self.distance, ss)) 
        return ss
        
    def Print(self):
        print ("WellName           %s" % self.Name)
        print ("PumpingRate        %s" % self.PumpingRate)
        print ("StorageCoefficient %s" % self.StorageCoefficient)
        print ("PumpingDuration    %s" % self.PumpingDuration)
        print ("Transmissivity     %s" % self.Transmissivity)
        for s in self.WellStrata:
           print (s.Name + "(" + str(s.Efficiency) + ")")
        print ("radius")
        print (self.radius)
        print ("settlement")
        print (self.settlement)
        print ("strata_drawdown")
        print (self.strata_drawdown)
        print ("strata_settlement")
        print (self.strata_settlement)
        print ("strata_emodulus")
        print (self.strata_emodulus) 
        print ("strata_changestress")
        print (self.strata_changestress) 
        
    def Print_tabular(self):
        print ("WellName", "PumpingRate","StorageCoefficient","Pumping Duration","Transmissivity")
        print (self.Name, self.PumpRate, self.StorageCoefficient, self.PumpingDuration,self.Transmissivity)
        
    def Print_drawdown(self, StrataName):
        i = 0
        for s in self.StrataNames:
            if (s == StrataName):
               print (self.strata_drawdown[self.strata_id])
               break
            i = i +1
class results():
        
    def __init__(self, Name):
        self.level_z = None
        self.Name = Name
        
    def setOutputDrawdownStrata(self, StrataName):
        self.StrataName = StrataName
        
    def writeSettlement (self, fname):
        fileOut = open(fname,"w")
        for i in range (0, len(self.x), 1):
            fileOut.write("%.2f,%.2f,%.6f\n"% (self.x[i],self.y[i],self.settlement[i]))
    def setSettlementLevel (self, z):
        self.level_z = z
        
    def writeDrawdown (self, fname):
        fileOut = open(fname,"w")
        for i in range (0, len(self.x), 1):
            fileOut.write("%.2f,%.2f,%.3f\n"% (self.x[i],self.y[i],self.strata_drawdown[i]))
        
    def Print(self):
        print ("Name %s"%(self.Name))
        print ("x                     y                   drawdown(%s)             settlement(total)"%(self.StrataName))
        for i in range (0, len(self.x), 1):
            print("%.3f             %.3f             %.3f                %.6f"%(self.x[i], self.y[i], self.strata_drawdown[i], self.settlement[i]))

class resultGrid(results):
    def __init__(self, Name, start_x, start_y, end_x, end_y, inc_x, inc_y):
           
        super(resultGrid, self).__init__(Name)
         
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.inc_x = inc_x
        self.inc_y = inc_y
        
        self.xcount = (self.end_x-self.start_x) / self.inc_x + 1 
        self.ycount = (self.end_y-self.start_y) / self.inc_y + 1
        
        self.size = int(self.xcount * self.ycount)
        
        self.x = np.zeros( (self.size), dtype=float)
        self.y =  np.zeros( (self.size), dtype=float)
        self.strata_drawdown = np.zeros( (self.size), dtype=float)
        self.settlement = np.zeros( (self.size), dtype=float)
        
       
    def readDewateringSite(self, ds):
        
        index = 0
        perc_prev = 0
        end_x1 = self.end_x + self.inc_x
        end_y1 = self.end_y + self.inc_y
 
        if self.level_z is not None:
            ds.setSettlementLevel (self.level_z)
        
        for x in range(self.start_x, end_x1, self.inc_x):
        
            for y in range (self.start_y, end_y1, self.inc_y): 
                
            #    print (x,y)   
                
                d = ds.getDrawdown (self.StrataName, x, y)
                s = ds.getSettlement (x, y)
            #   print ("resultGrid.readDewateringSite d:%s, s:%s" %(d, s))
               
                self.x[index] = x
                self.y[index] = y
                
                self.strata_drawdown[index] = d
                self.settlement[index] = s
                       
                perc = int(100 * index / self.size)
                # print (index)
        
                if (int(perc % 10) == 0 and perc != perc_prev): 
                    print ("%s read %s (%s%%) drawdown(%.2f) settlement(%.3f)"% (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), index, perc , self.strata_drawdown[index], self.settlement[index]))
                    perc_prev = perc
                
                index = index + 1
         
    def Print(self):
        for i in range (0, self.size + 1, 1):
            print ("%.2f,%.2f,%.3f\n"% (self.x[i],self.y[i],self.strata_drawdown[i]))

class resultPoints(results):
    
    def __init__(self, Name):
        super(resultPoints, self).__init__(Name)
       
        self.x = []
        self.y = []
        self.settlement = []
        self.strata_drawdown = []
    
    def addPoint(self, x, y):
        self.x.append(x)
        self.y.append(y)
        self.settlement.append(0.00)
        self.strata_drawdown.append(0.00)
        
    def readDewateringSite(self, ds):
        for i in range (0, len(self.x), 1):
            self.settlement[i] = ds.getSettlement (self.x[i], self.y[i])
            self.strata_drawdown[i] = ds.getDrawdown(self.StrataName, self.x[i], self.y[i])
  
        
   
class resultLine(results):
    
    def __init__(self, Name, start_x, start_y, end_x, end_y, inc_l):
        super(resultLine, self).__init__(Name)
        
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.inc_l = inc_l
        
        self.size = int(((self.end_x - self.start_x)**2 + (self.end_y - self.start_y)**2)**0.5 / self.inc_l)
              
        self.inc_x = (self.end_x - self.start_x) / self.size
        self.inc_y = (self.end_y - self.start_y) / self.size
        
        self.x = np.zeros( (self.size), dtype=float)
        self.y =  np.zeros( (self.size), dtype=float)
        self.strata_drawdown = np.zeros( (self.size), dtype=float)
        self.settlement = np.zeros( (self.size), dtype=float)
    
    def readDewateringSite(self, ds):
        
        xcounter = 0
        ycounter = 0
        index = 0
        perc_prev = ""
        

        
        for index in range(0, self.size, 1):
            
            x = self.start_x + self.inc_x * index
            y = self.start_y + self.inc_y * index
              
            d = ds.getDrawdown (self.StrataName, x, y)
            s = ds.getSettlement (x, y)
            #   print ("resultGrid.readDewateringSite d:%s, s:%s" %(d, s))
               
            self.x[index] = x
            self.y[index] = y
                
            self.strata_drawdown[index] = d
            self.settlement[index] = s
            
            perc = int(100 * index / self.size)
            
            if (int(perc % 10) == 0 and perc != perc_prev): 
                print ("%s read %s (%s%%) drawdown(%.2f) settlement(%.3f)"% (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), index, perc , self.strata_drawdown[index], self.settlement[index]))
                perc_prev = perc
     