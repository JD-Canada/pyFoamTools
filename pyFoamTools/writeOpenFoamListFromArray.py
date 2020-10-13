import os

def writeOpenFoamListFromArray(array,directory,fileName):

#    cwd=os.getcwd()
#    try:
#        os.mkdir(cwd+'\\'+'constant')
#
#    except FileExistsError:
#        print('constant directory already exists, passing without overwriting ...')
#        pass
#
#    try:
#    
#        os.mkdir(cwd+'\\'+'constant'+'\\'+'boundaryData')
#    except FileExistsError:
#        print('boundaryData directory already exists, passing without overwriting ...')
#        pass
    #print vector list
    
    if array.shape[1]==3:
        
        f= open(directory+'//'+fileName,"w+")
            
        f.write("%s\n" % str(array.shape[0]))
        f.write("(\n")
        
        for i in range(array.shape[0]):
            
            f.write("(%.5f %.5f %.5f)\n" % (array[i][0],array[i][1],array[i][2]))
        
        f.write(")")
        f.close()  
        print('Successfully wrote array to file.')
    
    #print scalar list
    if array.shape[1]==1:
        
        f= open(directory+'//'+fileName,"w+")
        
        f.write("%s\n" % str(array.shape[0]))
        f.write("(\n")
        
        for i in range(array.shape[0]):
            
            f.write("%.5f\n" % (array[i]))
        
        f.write(")")
        f.close()  
        print('Successfully wrote array to file.')

