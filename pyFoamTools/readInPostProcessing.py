
import os
from glob import glob
import decimal
import shutil 
import pandas as pd

import re
import pandas as pd


class readProbeFile():
    
    def __init__(self,path,treatedFilePath,dataType,variables,pointNames):
        
        self.path=path
        self.treatedFilePath=treatedFilePath
        self.probeType=dataType   
        self.vars=variables
        self.pointNames=pointNames
        
        if self.probeType == 'scalar':
            print('Reading file of scalar values ...')
            self.readData()
            self.addHeaders()
            
        if self.probeType == 'vector':
            self.readData()
            self.addHeaders()
            print('Reading file of vector values ...')
    
    def readData(self):
        self.treatedFile=open(self.treatedFilePath,'w')
        with open(self.path, 'r') as f:
            self.probeCount=0
            for line in f:
    
                if "Probe" in line:
                    self.probeCount=self.probeCount + 1
            
                line=line.replace(" (","")
                line=line.replace(")","")
                line=' '.join(line.split())
                self.treatedFile.write(line)
                self.treatedFile.write('\n')
        
        self.probeCount=self.probeCount-1        
        self.treatedFile.close()

        self.data=pd.read_csv(self.treatedFilePath,sep=' ',header=None,skiprows=self.probeCount+2,engine='python')

    def addHeaders(self):
        
        if self.probeType == 'vector':
            
            headers=['Time']
            
            for i in range(self.probeCount):
                headers.append('%s_%s'%(self.pointNames[i],self.vars[0]))
                headers.append('%s_%s'%(self.pointNames[i],self.vars[1]))
                headers.append('%s_%s'%(self.pointNames[i],self.vars[2]))

            self.data.columns=headers

        if self.probeType == 'scalar':
            
            headers=['Time']
            
            for i in range(self.probeCount):
                headers.append('%s_%s' %(self.pointNames[i],self.vars[0]))

            self.data.columns=headers

path=r'C:\Users\Jason\Desktop\p_rgh'
treatedFilePath=r'C:\Users\Jason\Desktop\treated'

a=readProbeFile(path,treatedFilePath,'scalar',['p'],pointNames=['Up','mid','down'])
data=a.data


#def get_vtk_files(path,basename,destinationPath):
