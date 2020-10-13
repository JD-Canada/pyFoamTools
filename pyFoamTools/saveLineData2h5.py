import numpy as np
import h5py
import threading
import os


"""
Compile all raw OpenFOAM line data into a single h5py file (saved to disk for easy reload).

The h5 format data will be saved to disk in the directory in which this script is run.
"""

#supply the path of the line data in the postProcessing folder of the case
#linePath=r'Z:\Jason\Projects\2020\EatonNordNumerics\PreSims\pre_0_09gradedWMLES_ani\postProcessing\uLine'
lookupPath=r'Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence\postProcessing\uLine'

os.chdir(lookupPath)
#supply a list of filenames for the lines to save to file. Saved h5 files will have these names.
lines=['a1_U','a2_U','a3_U','a1_s','a2_s','a3_s',]


def threadJob(path,lineName):
    """
    Call getLinePaths and saveLine2H5py in parallel
    """
        
    dataPaths=getLinePaths(path,lineName)
    saveLines2H5py(dataPaths,lineName)
    
def getLinePaths(path,lineName):
    
    """
    Recursively look through time step folders in path to find specified line name
    
    Returns a list of tuples, with the first entry the time step signature (e.g. '0.01')
    and the second the path to the corresponding .xy file.
    
    The returned list can be used with saveLines2h5py as the 'paths' argument.
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

def saveLines2H5py(paths,h5name):
    """
    Converts a list of tuples (time, path) indicating raw OpenFOAM line format data
    into a saved h5 file format.
    
    Use in conjunction with getLineData()
    """
    step=0
    h5 = h5py.File('%s.h5' % h5name, 'w')
    
    for t in paths:
        print(t)
        data=np.loadtxt(t[1],delimiter = " ")
        h5.create_dataset('%s' % step, data=data)
        step=step+1
        
    h5.close()


for line in lines:
    print(line)
    threading.Thread(target=threadJob, args=(lookupPath,line)).start()
