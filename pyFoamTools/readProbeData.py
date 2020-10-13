import os
from glob import glob
import decimal
import shutil 
import pandas as pd
import re
import pandas as pd


class readProbeFile():
    
    """Reads data from OpenFOAM probe data files in pandas dictionaries.
    
    Create a class for each file. Each probe data file can contain as many 
    sampling points as necessary. A new file will be saved (i.e., treatedFilePath) that contains 
    the same data as the original probe data file (path), but formatted in a more user-friendly 
    way. 
    
    """
    
    def __init__(self,path,treatedFilePath,dataType,variables,pointNames):
        
        ## Path to OpenFOAM probe data file
        self.path=path
        
        ## Path and file name for formatted data export
        self.treatedFilePath=treatedFilePath
        
        ## Probe data type (either 'vector' or 'scalar')
        self.probeType=dataType   
        
        ## Names of variables as strings in a comma separated list
        self.vars=variables
        
        ## Names of points as strings in a comma separated list
        self.pointNames=pointNames
        
        if self.probeType == 'scalar':
            print('Reading file of scalar values ...')
            self.readData()
            self.addHeaders()
            self.getPointData()
            
        if self.probeType == 'vector':
            print('Reading file of vector values ...')

            self.readData()
            self.addHeaders()
            self.getPointData()
    
    def readData(self):
        """Makes and opens a new to write formatted data, then writes
        the data to file and reads the file into a pandas dataframe.
        """
        
        ## Instance of the file to be written to
        self.treatedFile=open(self.treatedFilePath,'w')
        with open(self.path, 'r') as f:
            
            ## Number of probes as read from the file header
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

        ## Contents of the probe data file in a clean headersless dataframe
        self.data=pd.read_csv(self.treatedFilePath,sep=' ',header=None,skiprows=self.probeCount+2,engine='python')

    def addHeaders(self):
        
        """Adds headers to dataframe(s)
        """
        ## Dictionary containing headers for each specific point (key referenced). Contains as many keys as probe points.
        self.pointColumns={}
        
        if self.probeType == 'vector':
            
            ## Column headers for entire dataframe
            self.headers=['Time']
            
            for i in range(self.probeCount):
                
                #A list of column headers for each key
                self.pointColumns[self.pointNames[i]]=[]
                self.pointColumns[self.pointNames[i]].append('%s_%s'%(self.pointNames[i],self.vars[0]))
                self.pointColumns[self.pointNames[i]].append('%s_%s'%(self.pointNames[i],self.vars[1]))
                self.pointColumns[self.pointNames[i]].append('%s_%s'%(self.pointNames[i],self.vars[2]))
                
                self.headers.append('%s_%s'%(self.pointNames[i],self.vars[0]))
                self.headers.append('%s_%s'%(self.pointNames[i],self.vars[1]))
                self.headers.append('%s_%s'%(self.pointNames[i],self.vars[2]))

            self.data.columns=self.headers

        if self.probeType == 'scalar':
            
            self.headers=['Time']
            
            for i in range(self.probeCount):
                self.pointColumns[self.pointNames[i]]=[]
                self.pointColumns[self.pointNames[i]].append('%s_%s'%(self.pointNames[i],self.vars[0]))
                self.headers.append('%s_%s' %(self.pointNames[i],self.vars[0]))

            self.data.columns=self.headers
            
    def getPointData(self):
        
        """Places data for each point in a dictionary (self.pointData) organized by
        point 'keys'. 
        """

        ## Dictionary containing each point's data under its specific key.
        self.pointData={}
        
        for point in self.pointNames:
            self.pointData[point]={} 

            temp=['Time']
            for var in self.pointColumns[point]:
                temp.append(var)
            self.pointData[point]=self.data[temp]
                
    
    
    
    
    
    
    
    