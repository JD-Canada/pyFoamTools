
import os

from glob import glob
import threading
import shutil 
import numpy as np
import h5py
import pandas as pd
from scipy.spatial.transform import Rotation as R


class FileProcessing():
    
    """
    Processes the raw data in the postProcessing folder of an OpenFOAM case. Runs in parallel to save time. 
    
    Specifically:
        - orders .vtp files into a single directory increasing in chronological order
        - places all .xy format lines into h5 format. 

    A new folder called "postProcessingOrdered" appears in the main case directory. Subfolders will appear within this folder for "surfaces" and "lines". A subsubfolder will appear for each surface name, within which all the *.vtp will appear. The h5 line data will all appear within a subfolder of postProcessingOrdered called 'lines'. Because the surfaces are chronologically ordered, they can be easily loaded into Paraview to make animations, or do some other analysis.  
    
    """
    
    def __init__(self,casePath):

        """
        Calls findItems() and createProcessFolder()
        """
        print('hi')
        self.casePath=casePath
        self.findItems()
        self.createProcessedFolder()

    def findItems(self):
        
        """
        Find information on each type of postProcessing item in the postProcessing folder (e.g. .vtp surfaces and their names, .xy format lines and their names).
        
        Returns a dictionary (processingItems) with a key for each type (surface or line) and a subkey for each line or surface. The 
        """    

        ## (str) Path to the postProcessing folder of the OpenFOAM case
        self.postProcessingPath=self.casePath+"\\"+"postProcessing"

        ## (dict) Contains names (keys) for each surface and line in the postprocessing folder
        self.processingItems={}
        
        items=next(os.walk(self.postProcessingPath))[1]
       
        for item in items:
            try:

                #get path to first time step in folder
                firstTime=next(os.walk(self.postProcessingPath+"\\"+item))[1][0]
                
                #concatenate path to first time step
                subFolderPath=self.postProcessingPath+"\\"+item+"\\"+firstTime
                
                ## (list) Paths to each *.xy file in the first time-step's folder
                self.linePaths=glob("%s\\*.xy"%subFolderPath)
                
                # check to see if there are lines in postProcessing folder
                if self.linePaths:
                    print("Found *.xy type lines in %s folder" %item)
                    
                    #add key called 'xylines' to dictionary
                    self.processingItems['xylines']={}

                    for path in self.linePaths:
                        
                        head,tail = os.path.split(path)
                        self.processingItems['xylines'][tail.split(".")[0]]=self.postProcessingPath+"\\"+item
                
                # check to see if there are surfaces in the folder
                self.surfaceNames=glob("%s\\*.vtp"%subFolderPath)

                if self.surfaceNames:
                    
                    print("Found *.vtp type surfaces in %s folder" %item)
                    
                    #self.surfacePath=self.postProcessingPath+"\\"+"postProcessing"+"\\"+item
                   
                    self.processingItems['vtpSurfaces']={}
                    
                    for path in self.surfaceNames:
                        head,tail = os.path.split(path)
                        self.processingItems['vtpSurfaces'][tail.split(".")[0]]=self.postProcessingPath+"\\"+item
                                    
            except IndexError:
                pass
            
        print('Found a total of %d *.xy lines' %len(self.processingItems['xylines']))
        print('Found a total of %d *.vtp surfaces' %len(self.processingItems['vtpSurfaces']))
        

    def createProcessedFolder(self):
        """
        Creates a folder called 'postProcessingOrdered' in case directory if it does not already exist.
        """

        self.processedPath=self.casePath+"\\"+"postProcessingOrdered"
        try:
            os.stat(self.processedPath)
        except:
            print('made a new directory')
            os.system("mkdir %s " % self.processedPath)

    def processVtpSurfacesSerial(self):
        
        """
        Calls get_vtp_files in serial to copy chronologically renamed vtp files in their appropriate directory in postProcessingOrdered/surfaces folder
        """

        if 'vtpSurfaces' in self.processingItems:
               
            for name,path in self.processingItems['vtpSurfaces'].items():
                destinationPath=self.processedPath+"\\"+"surfaces"+"\\"+name
                os.system("mkdir %s" %destinationPath)
                times,paths,result=self.get_vtp_files(path,name,destinationPath)
                #threading.Thread(target=self.threadedOrderVtpFiles, args=(path,name,destinationPath)).start()

    def processVtpSurfacesParallel(self):
        
        """
        Calls threadedOrderVtpFiles in parallel to copy chronologically renamed vtp files in their appropriate directory in postProcessingOrdered/surfaces folder
        """

        if 'vtpSurfaces' in self.processingItems:
               
            for name,path in self.processingItems['vtpSurfaces'].items():
                destinationPath=self.processedPath+"\\"+"surfaces"+"\\"+name
                os.system("mkdir %s" %destinationPath)
                threading.Thread(target=self.threadedOrderVtpFiles, args=(path,name,destinationPath)).start()


                
    def threadedOrderVtpFiles(self,path,name,destinationFolder):

        """
        Called to run self.get_vtp_files() in parallel. Running in parallel saves a lot of time, especially if there are numerous surfaces, each with numerous time steps. 
        """

        times,paths,result=self.get_vtp_files(path,name,destinationFolder)
        
    def get_vtp_files(self,path,basename,destinationPath):

        """Recursively looks in path specified for .vtk files including the basename, renames them to be ordered chronologically, then places them in postProcessingOrdered/surfaces/surfaceName so they can be read into Paraview in a useable way, for example to make animations. 
        
        Args:
        path      (str): Directory to recursively look in.
        basename  (str): basename common all .vtp files in each directory (e.g. 'U_slice' .vtp) 
        destinationPath (str): folder where the renamed vtp files will be placed
        """
        
        result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.vtp'))]
        times = [ float(os.path.basename(f.path)) for f in os.scandir(path) if f.is_dir() ]
        times.sort()
        times=list(map(str, times))
    
        orderedList=[]
    
        print('Ordering vtp files for surface "%s" ...' % basename)
        for count, time in enumerate(times):
            
            for i in result:
    
                if '\\'+time+'\\' in i:
                    
                    if (basename in i):
                        orderedList.append(i)
                        
                elif time.split('.')[1] == '0' and '\\'+time.split('.')[0]+'\\' in i:

                    if (basename in i):
                        orderedList.append(i)
                        
        print('Ordering vtp files for surface "%s" complete.' % basename)
                       
        for count, file in enumerate(orderedList):
            basename=os.path.basename(file)
            basename=os.path.splitext(basename)[0]
            basename2=basename.replace('_','')
            newname=basename2+'%s.vtp' %str(count).zfill(5)
            print('Renaming "%s" to "%s" and copying ...' %(basename,newname))
            
            
            destinationFilePath=destinationPath+"\\"+newname
            shutil.copyfile(file, destinationFilePath) 
            
        return(times,orderedList,result)


    def getLinePaths(self,path,lineName):
        
        """
        Recursively look through time step folders in path to find specified line name
        
        Returns a list of paths for each .xy file corresponding to each time-step ordered chronologically. 
        
        The returned list can be used with saveLines2H5py() as the 'paths' argument.
        """    
        
        times=[]
        paths=[]
        print(path)
    
        for root, dirs, files in os.walk(path):
            """
            This is slow, which is why I was worried about having 400k lines...
            """
            
            for file in files:
        
                
                if "%s.xy" % lineName in file:
                    print(lineName)
                    times.append(float(os.path.basename(root)))
                    paths.append(root+"\\"+file)
                    
        zipped=zip(times,paths)
        
        return sorted(zipped)


    def processXYlinesSerial(self):

        """
        Calls threadedSaveLineData2h5() in serial to place line data in h5 format files within the postProcessingOrdered/lines folder. 
        """

        if 'xylines' in self.processingItems:
            
            destinationPath=self.processedPath+"\\"+"lines"
            os.system("mkdir %s" %destinationPath)
            
            for name,path in self.processingItems['xylines'].items():
                
                dataPaths=self.getLinePaths(path,name)
                self.saveLines2H5py(path,name,destinationPath)

#                threading.Thread(target=self.threadedSaveLineData2h5, args=(path,name,destinationPath)).start()

    def processXYlinesParallel(self):

        """
        Calls threadedSaveLineData2h5() in parallel to place line data in h5 format files within the postProcessingOrdered/lines folder. 
        """

        if 'xylines' in self.processingItems:
            
            destinationPath=self.processedPath+"\\"+"lines"
            os.system("mkdir %s" %destinationPath)
            
            for name,path in self.processingItems['xylines'].items():

                threading.Thread(target=self.threadedSaveLineData2h5, args=(path,name,destinationPath)).start()
        
        
    def threadedSaveLineData2h5(self,path,lineName,destinationPath):
        """
        Call getLinePaths and saveLine2H5py in parallel
        """
            
        dataPaths=self.getLinePaths(path,lineName)
        self.saveLines2H5py(dataPaths,lineName,destinationPath)
        
    def saveLines2H5py(self,paths,h5name,destinationPath):
        """
        Places .xy line data into h5 format. Data is added in the order of the list of paths. 
        """
        step=0
        h5 = h5py.File('%s\\%s.h5' % (destinationPath,h5name), 'w')
        
        for t in paths:
            print(t)
            data=np.loadtxt(t[1],delimiter = " ")
            h5.create_dataset('%s' % step, data=data)
            step=step+1
            
        h5.close()
    
    def sortChronoH5Keys(self,h5Instance):
        """
        Returns a list of chronologically sorted keys (i.e. time-steps) in an h5 file
        """
        keys=list(h5Instance.keys())
        
        #convert to int
        intKeys = [int(x) for x in keys]
        
        #sort chronologically
        sortedIntKeys=sorted(intKeys)
        
        #convert back to string and return
        return [str(x) for x in sortedIntKeys]

    
    def zipXYlineFolder(self):
        os.chdir(self.postProcessingPath)
        os.system('tar -czvf uLine.tar.gz uLine')


    def extractProfilePoint(self,pos,h5Instance,keys,datatype):
    
        if datatype=='scalar':
            p=[]
            t=[]
            s=[]
            
            for key in keys:
                #2 for sediment, 1 for k
                t.append(float(key))
                p.append(h5Instance[key][pos,0])
                s.append(h5Instance[key][pos,2])
    
            p=np.asarray(p)
            t=np.asarray(t)  
            s=np.asarray(s)
            ensemble=np.vstack((p,t,s))
            return np.transpose(ensemble)
           
        if datatype=='vector':
            p=[]
            t=[]
            u=[]
            v=[]
            w=[]
            
            for key in keys:
                p.append(h5Instance[key][pos,0])
                t.append(float(key))
                u.append(h5Instance[key][pos,1])
                v.append(h5Instance[key][pos,2])
                w.append(h5Instance[key][pos,3])
            p=np.asarray(p)
            t=np.asarray(t)  
            u=np.asarray(u)
            v=np.asarray(v)
            w=np.asarray(w)
            
            ensemble=np.vstack((p,t,u,v,w))
            return np.transpose(ensemble)

    def getScalarDataAlongProfile(self,h5File):
        
        profileData={}
        keys=self.sortChronoH5Keys(h5File)

        for i in range(h5File['0'].shape[0]):
            try:
                
                profileData[str(i)]=pd.DataFrame(self.extractProfilePoint(i,h5File,keys,'scalar'))
                profileData[str(i)].columns=['z','t','s']
                
            except ValueError:
                break
        
        return profileData


    def getVectorDataAlongProfile(self,h5File):
        
        profileData={}
        keys=self.sortChronoH5Keys(h5File)

        for i in range(h5File['0'].shape[0]):
            try:
                
                profileData[str(i)]=pd.DataFrame(self.extractProfilePoint(i,h5File,keys,'vector'))
                profileData[str(i)].columns=['z','t','u','v','w']
            except ValueError:
                break
        
        return profileData

    def getCorrScalarVectorAlongProfile(self,vectorData,scalarData):
        
        z=[]
        su=[]
        sv=[]
        sw=[]  
        
        for point in vectorData:

            su.append(np.corrcoef(scalarData[point]['s'],vectorData[point]['u'])[0][1])
            sv.append(np.corrcoef(scalarData[point]['s'],vectorData[point]['v'])[0][1])
            sw.append(np.corrcoef(scalarData[point]['s'],vectorData[point]['w'])[0][1])

            z.append(vectorData[point]['z'][0])
                
        zND=(z-min(z))/(max(z)-min(z))
        df=pd.DataFrame([z,zND,su,sv,sw])
        df=df.transpose()
        df.columns=['z','zND','su','sv','sw']

        return df    


    def getCorrAlongProfile(self,profileData):
        
        z=[]
        uv=[]
        uw=[]
        vw=[]  
        
        for point in profileData:

            uv.append(np.corrcoef(profileData[point]['u'],profileData[point]['v'])[0][1])
            uw.append(np.corrcoef(profileData[point]['u'],profileData[point]['w'])[0][1])
            vw.append(np.corrcoef(profileData[point]['v'],profileData[point]['w'])[0][1])

            z.append(profileData[point]['z'][0])
                
        zND=(z-min(z))/(max(z)-min(z))
        df=pd.DataFrame([z,zND,uv,uw,vw])
        df=df.transpose()
        df.columns=['z','zND','uv','uw','vw']

        return df     

    def rotateUCompsAlongProfile2NewAxis(self,profileData,names,axisOfRot,cosine):
        
        rotatedData={}
        
        for point in profileData:
            r=R.from_euler(axisOfRot,cosine)
            rotatedData[point]=profileData[point][['z','t']]
            rotVect=r.apply(profileData[point][[names[0],names[1],names[2]]])
            rotatedData[point][names[0]]=rotVect[:,0]
            rotatedData[point][names[1]]=rotVect[:,1]
            rotatedData[point][names[2]]=rotVect[:,2]
        
        return rotatedData  

    def getMeanScalarAlongProfile(self,profileData):
        
        sMean=[]
        z=[]
        
        for point in profileData:

            sMean.append(profileData[point]['s'].mean())
            z.append(profileData[point]['z'][0])
                
        zND=(z-min(z))/(max(z)-min(z))
        df=pd.DataFrame([z,zND,sMean])
        df=df.transpose()
        df.columns=['z','zND','sMean']

        return df             

    def getVarScalarAlongProfile(self,profileData):
        
        sStd=[]
        z=[]
        
        for point in profileData:

            sStd.append(profileData[point]['s'].std())
            z.append(profileData[point]['z'][0])
                
        zND=(z-min(z))/(max(z)-min(z))
        df=pd.DataFrame([z,zND,sStd])
        df=df.transpose()
        df.columns=['z','zND','sStd']

        return df  
        
    def getMeanUCompsAlongProfile(self,profileData):
        
        uMean=[]
        vMean=[]
        wMean=[]
        z=[]
        
        for point in profileData:

            uMean.append(profileData[point]['u'].mean())
            vMean.append(profileData[point]['v'].mean())
            wMean.append(profileData[point]['w'].mean())
            
            z.append(profileData[point]['z'][0])
                
        zND=(z-min(z))/(max(z)-min(z))
        df=pd.DataFrame([z,zND,uMean,vMean,wMean])
        df=df.transpose()
        df.columns=['z','zND','uMean','vMean','wMean']

        return df             
        
    def getVarUCompsAlongProfile(self,profileData):
        
        uStd=[]
        vStd=[]
        wStd=[]
        z=[]
        
        for point in profileData:

            uStd.append(profileData[point]['u'].std())
            vStd.append(profileData[point]['v'].std())
            wStd.append(profileData[point]['w'].std())
            
            z.append(profileData[point]['z'][0])
                
        zND=(z-min(z))/(max(z)-min(z))
        df=pd.DataFrame([z,zND,uStd,vStd,wStd])
        
        df=df.transpose()
        df.columns=['z','zND','uStd','vStd','wStd']
        df['tStd']=df['uStd']+df['vStd']+df['wStd']

        return df           
        

# process=FileProcessing(r"Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence")  
