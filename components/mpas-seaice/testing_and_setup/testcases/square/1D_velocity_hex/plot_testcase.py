from netCDF4 import Dataset
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.collections import PatchCollection
import numpy as np


operatorMethod = "wachspress"
subcycleNumber = 7680
#filenameIn = "./output_quad_%s_%i/output.2000.nc" %(operatorMethod,subcycleNumber)
filenameIn = "./output/output.2000.nc"

iTime = -1

# read in file
filein = Dataset(filenameIn,"r")

nCells = len(filein.dimensions["nCells"])
nVertices = len(filein.dimensions["nVertices"])
vertexDegree = len(filein.dimensions["vertexDegree"])

cellsOnVertex = filein.variables["cellsOnVertex"][:]
cellsOnVertex -= 1


xVertex = filein.variables["xVertex"][:]
yVertex = filein.variables["yVertex"][:]

xCell = filein.variables["xCell"][:]
yCell = filein.variables["yCell"][:]

uVelocity = filein.variables["uVelocity"][iTime,:]
vVelocity = filein.variables["vVelocity"][iTime,:]

stressDivergenceU = filein.variables["stressDivergenceU"][iTime,:]
stressDivergenceV = filein.variables["stressDivergenceV"][iTime,:]

try:
    principalStress1 = filein.variables["principalStress1Var"][iTime,:,2]
except:
    principalStress1 = filein.variables["principalStress1Weak"][iTime,:]

try:
    principalStress2 = filein.variables["principalStress2Var"][iTime,:,2]
except:
    principalStress2 = filein.variables["principalStress2Weak"][iTime,:]

filein.close()

xmin = np.amin(xCell)
xmax = np.amax(xCell)
ymin = np.amin(yCell)
ymax = np.amax(yCell)

fileGrid = Dataset("grid_0081.nc","r")
Lx = fileGrid.Lx
Ly = fileGrid.Ly
fileGrid.close()

# get patches list
patchesVertex = []
deletedVertices = []
for iVertex in range(0,nVertices):
    vertices = []
    useVertex = True
    for iCellOnVertex in range(0,vertexDegree):
        iCell = cellsOnVertex[iVertex,iCellOnVertex]
        if (iCell != -1):
            vertices.append((xCell[iCell],yCell[iCell]))
        else:
            useVertex = False
    if (useVertex):
        patchesVertex.append(Polygon(vertices,True))
    else:
        deletedVertices.append(iVertex)
deletedVertices = np.array(deletedVertices)

uVelocity = np.delete(uVelocity, deletedVertices)
stressDivergenceU = np.delete(stressDivergenceU, deletedVertices)
principalStress1 = np.where(principalStress1 < 1e20, principalStress1, 0.0)
principalStress2 = np.where(principalStress2 < 1e20, principalStress2, 0.0)

# patch collections
pcUVelocity = PatchCollection(patchesVertex, cmap=plt.get_cmap("jet"))
pcUVelocity.set_array(uVelocity)

pcStressDivergenceU = PatchCollection(patchesVertex, cmap=plt.get_cmap("jet"))
pcStressDivergenceU.set_array(stressDivergenceU)

# plot
domain1 = Rectangle((0,0),Lx,Ly,linewidth=0.1,edgecolor='k',facecolor='none')
domain2 = Rectangle((0,0),Lx,Ly,linewidth=0.1,edgecolor='k',facecolor='none')

fig, axes = plt.subplots(2,2)

axes[0,0].add_collection(pcUVelocity)
axes[0,0].set_xlim((xmin,xmax))
axes[0,0].set_ylim((ymin,ymax))
axes[0,0].set_aspect('equal')
axes[0,0].add_patch(domain1)

axes[0,1].add_collection(pcStressDivergenceU)
axes[0,1].set_xlim((xmin,xmax))
axes[0,1].set_ylim((ymin,ymax))
axes[0,1].set_aspect('equal')
axes[0,1].add_patch(domain2)

axes[1,0].scatter(principalStress1, principalStress2, s=1, c="k")
axes[1,0].set_aspect('equal')

axes[1,1].axis('off')



plt.savefig("plot.png",dpi=600)
