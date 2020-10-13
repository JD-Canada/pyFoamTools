
import numpy as np
import pandas as pd
import numpy as np
from stl import mesh

#Raw xyz data points from Pascale's work
data=pd.read_csv(r"C:\Users\Jason\Google Drive\Concordia_2020\MitisNeigette\CAD\mitisNeigetteLidarBed.csv", sep="\t",header=(0))

data=data[['Xnew','Ynew','Z_lit_vrai']]
data.columns=['x','y','z']

#Make the numbers smaller so they are easier to work with
xmin=258009-data.x.min()
xmax=258131-data.x.min()

ymin=5376456-data.y.min()
ymax=5376583-data.y.min()

zBottom=data.z.min()-1

#upper limit of boundary stl files
zTop=75

data['x_shifted']=data.x-data.x.min()
data['y_shifted']=data.y-data.y.min()

#This file is used in MeshLab to make the .stl file of the bathymetry
data.to_csv('rawLidarPlusBathy.xyz', sep=' ',header=False,index=False,columns=['x_shifted','y_shifted','z'])


#Function used to build and export stl file
def buildStl(faces,vertices,fileName):
    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[f[j],:]
    
    # Write the mesh to file "cube.stl"
    cube.save('%s.stl' %fileName)


"""
Make stl file for Mitis upstream boundary condition
"""
# Define the 8 vertices of the cube (0 indexed) in the shifted coordinate space
verticesMitis = np.array([\

    [151, 69, zBottom],
    [108, 57, zBottom],
    [108, 57, zTop],
    [151, 69, zTop]])
    
# Define the 2 triangles using only the vertices of the upstream face of the cube
facesMitis = np.array([[0,1,2],[0,2,3]])

# Build stl file
buildStl(facesMitis,verticesMitis,'mitisBoundary')


"""
Draw stl file for Neigette upstream condition
"""
# Define the 8 vertices of the cube
verticesNeigette = np.array([\
    [92, 61, zBottom],
    [64, 86, zBottom],

    [64, 86, zTop],
    [92, 61, zTop]])

facesNeigette = np.array([[0,1,2],[0,2,3]])
buildStl(facesNeigette,verticesNeigette,'neigetteBoundary')

"""
Draw stl file for far downstream condition
"""
# Define the 8 vertices of the cube
verticesDownstream = np.array([\
    [126, 176, zBottom],
    [73, 161, zBottom],
    [73, 161, zTop],
    [126, 176, zTop]]
)

facesDownstream = np.array([[1,0,2],[0,3,2]])
buildStl(facesDownstream,verticesDownstream,'farDownstream')


"""
Draw stl file for near downstream condition
"""
# Define the 8 vertices of the cube
verticesDownstream = np.array([\
    [75, 136, zBottom],
    [135, 154, zBottom],
    [135, 154, zTop],
    [75, 136, zTop]]
)

facesDownstream = np.array([[1,0,2],[0,3,2]])
buildStl(facesDownstream,verticesDownstream,'nearDownstream')

"""
Draw stl file for top condition
"""
# Define the 8 vertices of the cube
verticesDownstream = np.array([\
    [126, 176, zBottom],
    [73, 161, zBottom],
    [73, 161, zTop],
    [126, 176, zTop]]
)

# Define the 10 triangles composing the cube without the bottom
facesDownstream = np.array([[1,0,2],[0,3,2]])
buildStl(facesDownstream,verticesDownstream,'downstream')

