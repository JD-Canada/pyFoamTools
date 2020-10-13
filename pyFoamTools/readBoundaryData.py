import pandas as pd
import os 

class readBoundaryData():
    
    """
    Reads in data placed in ./constant/boundaryData. This format is useful for 
    timeVaryingMappedFixedValue boundary conditions or the turbulentDFSEMInlet
    boundary condition.
    
    The data on a boundary patch can be export using by including a 'sample' file in 
    the system folder with this format:
        
        /*--------------------------------*- C++ -*----------------------------------*\
        | =========                 |                                                 |
        | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
        |  \\    /   O peration     | Version:  4.0                                   |
        |   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
        |    \\/     M anipulation  |                                                 |
        \*---------------------------------------------------------------------------*/
        FoamFile
        {
            version     2.0;
            format      ascii;
            class       dictionary;
            object      sampleDict;
        }
        // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
        
        
        type surfaces;
        functionObjectLibs              ("libsampling.so");
        writeControl timeStep;
        writeInterval 1;
        enabled true;
        
        surfaceFormat boundaryData;
        interpolationScheme none;
        interpolate false;
        triangulate false;
        
        fields
        (
            U k omega R
        );
        
        surfaces 
        (
            inletSurface
            {
                type patch;
                patches (nInlet);
            }
            
            outletSurface
            {
                type patch;
                patches (nOutlet);
            }
            
        );        
        
    Calling this from the commandline with:
        
        pisoFoam -postProcess -func R -latestTime (run first to get R)
         
        postProcess -func sample -latestTime
        
        
    will export the U, k, omega and Reynolds stress tensor (R) to the postProcessing directory. 
    Other fields can also be exported in a similar fashion.
    
    
    This data can then be accessed in the dictionaries of the 'data' attribute of an instance of this class. 
    Perform the necessary operations on the fields in your python script and then export them to file. 
    This was useful for calculating the turbulent length scale using k and omega. 
     
    """
    
    def __init__(self,path):
        
        self.path=path
        self.boundaryDataPath=self.path+'/'+'constant/'+'boundaryData'
        
        self.getPatchDirs()
        self.readData()
        
    def getPatchDirs(self):
        self.patchSubfolders = [ f.path for f in os.scandir(self.boundaryDataPath) if f.is_dir() ]

    def readData(self):
        
        self.data={}
        
        for folder in self.patchSubfolders:
            
            
            time=os.path.basename(folder)
            
            print("Extracting for time %s" % time)
            
            patchName=os.path.basename(folder)
            self.data[patchName]={}
            
            pointPath= folder + "/points"
            
            self.data[patchName]['points'], self.data[patchName]['nmbPoints'] = self.readInData(pointPath)
            self.data[patchName]['points'].columns = ['x','y','z']
            
            times=os.listdir(folder)

            for time in times:
                if time == 'points':
                    continue
                else:
                    for field in os.listdir(folder+'/'+time):
                        self.data[patchName][field],self.data[patchName]['nmbPoints']=self.readInData(folder+'/'+time+'/'+field)
                        if field == "U":
                            self.data[patchName][field].columns = ['u','v','w']
                        if field == "R":
                            self.data[patchName][field].columns = ['xx','xy','xz','yy','yz','zz']
                        if field == "k":
                            self.data[patchName][field].columns = ['k']
                        if field == "omega":
                            self.data[patchName][field].columns = ['omega']

    def readInData(self,path):

        with open(path, 'r') as f:
            
            nmbPoints=None
            
            data=[]
            
            for line in f:
                
                line=line.replace("(","")
                line=line.replace(")","") 
                
                #skip empty lines
                if not line.strip():
                    continue
                
                #get number of points
                if len(line.split()) == 1:
                    
                    if nmbPoints is None:
        
                        nmbPoints=line
                        continue
                    
                data.append(line.split())
            
            data=pd.DataFrame(data).astype(float)
            
            return data, nmbPoints


#boundaryName='inletSurface'
#casePath=r'Z:\Jason\Projects\2020\MitisNeigette\cyclicTests\nPrecDFSEM'
#
#points=readBoundaryDataFile(casePath)
#bob=points.data
#print(points.subfolders)