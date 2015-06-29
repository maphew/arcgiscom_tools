'''
BinormalPoints.py

Authors
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug 18, 2008
Updates  June 2013

Requires:  random, math, py_gp_methods, PointMaker

Notes:
  random is used to generate random numbers, check the random module
  in the Python documentation for more details.  A random
  floating point number between 0 and 1 is created.  If you want numbers
  within a specific range, then you can use uniform( a, b) where N is the
  number generated within the range defined by a and b.

  function  points created

  onUC      on the circumference of the circle
  inUC      within the circle
'''

#-----------------------------------------------------------------------------
#Main
#
import os, sys, string, math, random
import PointMaker as PM
import py_gp_methods as py_gp
#
import arcpy
#
arcpy.overwriteOutput = True
#
#inputs
#
binomCent = sys.argv[1]      #center
Xstd = sys.argv[2]           #stand. dev of X
Ystd = sys.argv[3]           #stand. dev of Y
Rho = sys.argv[4]            #correlation coefficient
n = int(sys.argv[5])         #number of points
numShapes = int(sys.argv[6]) #number of shapes to create
outFC = sys.argv[7]          #output shapefile
outCSV = sys.argv[8]
arcpy.Extent = sys.argv[9]      #output extent
outToScreen = sys.argv[10]   #output results to screen
#
#checks
#
#center check
try:
  aPair = string.split(binomCent," ")
  Xcent = float(aPair[0]); Ycent = float(aPair[1])
  arcpy.AddMessage("\n" + "Shapes centered at " + str(aPair))
  binomCent = "fixed"
except:
  arcpy.AddMessage("\n" + "Shapes centered randomly within dataframe extent")
  binomCent = "random"
#
#  Stats check
binorm_stat = False
binorm_rho = False
try:
  Xstd = float(Xstd); Ystd = float(Ystd)
except:
  binorm_stat = True
  arcpy.AddMessage("Binormal distribution will be created using random stats")
try:
  Rho = float(Rho)
  if (Rho > 1.0) or (Rho < -1.0):
    msg = "Correlation coefficient needs to be between -1.0 and 1.0"
    arcpy.AddMessage("\n" + msg)
    sys.exit()  
except:
  binorm_rho = True
  arcpy.AddMessage("Binormal distribution will be created using random correlation")
#    
#  n and numshapes check              
try:
  n = abs(int(n)); numShapes = abs((numShapes))
  if (n == 0) or (numShapes == 0):
    arcpy.AddMessage("No shapes created and/or points per shape is zero")
    sys.exit()
except:
  arcpy.AddMessage("Improper entry for number of features or points per feature")
  sys.exit()
#
#  Extent check
#
L, R, B, T = py_gp.gp_extent(arcpy)  # get the extent if any
#
#output check
#
if (outFC == "#") and (outCSV == "#"):
  outToScreen = "true"
  aMsg = "\n" + "No shapefile or csv file created..." + \
         "so output is directed to screen"
  arcpy.AddMessage(aMsg)
#
#end checks
#
if outFC != "#":
  outFC = outFC.replace("\\","/")
  fullName = os.path.split(outFC)
  outFolder = fullName[0].replace("\\", "/")
  shapeClass = "Point"
#
#collect the points
#
outPnts = []
for i in range(numShapes):
  if (binomCent == "random"):
    if numShapes > 1: 
      Xcent = random.uniform(L,R); Ycent = random.uniform(B,T)
    else:
      Xcent = L + ((R-L)/2.0); Ycent = B + ((T-B)/2.0)
  if binorm_stat == True:
    bin_max = (R - L) * 0.05  #max is 5%  of width
    bin_min = (R - L) * 0.001 #min is 0.1% of width
    Xstd = random.uniform(bin_min, bin_max)
    Ystd = Xstd * random.random()
  if (binorm_rho == True):
    Rho = random.uniform(-1.0, 1.0)
  #
  #generate the points
  #
  pnts = PM.binormal(n, Xcent, Ycent, Xstd, Ystd, Rho)
  #
  outPnts.append(pnts)
#
#optional shapefile creation
if outFC != "#":
  fieldsToAdd = [["Group", "LONG", "9", "#"],
                 ["X", "DOUBLE", 16, 7],
                 ["Y", "DOUBLE", 16, 7]]
  py_gp.createPointFile (outFC, shapeClass, "#", outPnts, fieldsToAdd, arcpy)
  arcpy.AddMessage("\n" + "You can join the original table to " \
                + "this shapefile table if you want other attributes." + "\n")
#
#optional csv file creation or output to screen
if outCSV != "#":
  PM.to_CSV(outCSV, outPnts)
#
if outToScreen == "true":
  py_gp.print_pnts(outPnts, arcpy)
  
  
