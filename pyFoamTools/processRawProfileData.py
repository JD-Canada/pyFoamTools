import os
import glob

"""
This script postprocesses numerous OpenFOAM uLine files
"""

linePath=r'Z:\Jason\Projects\2020\EatonNordNumerics\PreSims\pre_uni0_05_cyclicSidesRoughULES\postProcessing\lineTests'
os.chdir(r'C:\Users\Jason\Desktop\New Folder')

fileNames,namesExt=getFileNames(linePath)

def getFileNames(linePath):
    for root, dirs, files in os.walk(linePath):
        fileNames=[]
        for dirname in sorted(dirs, key=float):
            names = [os.path.basename(x) for x in glob.glob(root+'\\'+dirname+'\\'+'*.xy')]
            for name in names:
                fileNames.append(name.split('.')[0])
            return fileNames,names
        
for name in names:
    os.system('mkdir %s' % name)
    
#move files
    
def moveFiles(linePath,namesExt):
    for root, dirs, files in os.walk(linePath):
        
        for dirname in sorted(dirs, key=float):
            
            for name in namesExt:
                print('cp %s\%s\%s .\%s' %(linePath,dirname,name,name.split('.')[0]))
                os.system('cp %s\%s\%s .\%s' %(linePath,dirname,name,name.split('.')[0]))

moveFiles(linePath,namesExt)