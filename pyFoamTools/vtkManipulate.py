# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 12:04:50 2020

@author: Jason
"""
import os
from glob import glob
import shutil 


path=r"Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence\postProcessing\sampledSurface"
newPathM1=r"Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence\postProcessing\m1"
#newPathM2=r"Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence\postProcessing\m2"
#newPathApex=r"Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence\postProcessing\nearApex"
#newPathTop=r"Z:\Jason\Projects\2020\MitisNeigette\MainSims\confluence\postProcessing\top"


times,paths,result=get_vtk_files(path,'m1',newPathM1)
#times,paths,result=get_vtk_files(path,'m2',newPathM2)
#times,paths,result=get_vtk_files(path,'nearApex',newPathApex)
#
#times,paths,result=get_vtk_files(path,'top',newPathTop)


def get_vtk_files(path,basename,destinationPath):
    """Recursively look in path specified for .vtk files including the basename. 
    
    Args:
    path      (str): Directory to recursively look in.
    basename  (str): basename common all .vtp files in each directory (e.g. 'U_slice' .vtp) 
    
    """
    
    result = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.vtp'))]
    times = [ float(os.path.basename(f.path)) for f in os.scandir(path) if f.is_dir() ]
    times.sort()
    times=list(map(str, times))

    orderedList=[]

    for count, time in enumerate(times):
        
        for i in result:

            if '\\'+time+'\\' in i:
                
                if (basename in i):
                    print(time)
                    print(i)
                    orderedList.append(i)
                    

            elif time.split('.')[1] == '0' and '\\'+time.split('.')[0]+'\\' in i:
                print('------')
                print(time)
                if (basename in i):
                    print(basename)
                    print(i)
                    orderedList.append(i)
                   
    for count, file in enumerate(orderedList):
        basename=os.path.basename(file)
        basename=os.path.splitext(basename)[0]
        basename=basename.replace('_','')
        print("Copying file %s" %basename)
        newname=basename+'%s.vtp' %str(count).zfill(5)
        
        destinationFilePath=destinationPath+"\\"+newname
        shutil.copyfile(file, destinationFilePath) 
        
    return(times,orderedList,result)
    

    
    
    
    
    