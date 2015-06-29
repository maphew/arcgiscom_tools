'''
CirclePoints.py

Authors
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug 18, 2008
Modified June 2013

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
import arcpy

arcpy.overwriteOutput = True
#
#inputs
theType = string.split(sys.argv[1]," ")[0]
circCent = sys.argv[2]
radius = sys.argv[3]
n = sys.argv[4]              #number of points
numShapes = sys.argv[5]      #number of shapes to create
outFC = sys.argv[6]          #output shapefile
outCSV = sys.argv[7]
arcpy.Extent = sys.argv[8]      #output extent
outToScreen = sys.argv[9]    #output results to screen
#
#checks
#
try:  #center check
  aPair = string.split(circCent," ")
  Xcent = float(aPair[0]); Ycent = float(aPair[1])
  arcpy.AddMessage("\n" + "Shapes centered at " + str(aPair))
  circCent = "fixed"
except:
  arcpy.AddMessage("\n" + "Shapes centered randomly within dataframe extent")
  circCent = "random"
#
try:  #radius check
  radius = float(radius)
  if radius == 0.0:
    arcpy.AddMessage("A zero radius is not permitted")
    sys.exit()
  elif radius < 0.0:
    arcpy.AddMessage("Random radii between 1 and 100 will be used")
  else:
    arcpy.AddMessage("Circles will be created using a radius of " + str(radius))
except:
  arcpy.AddMessage("Invalid radius entry")
  sys.exit()
#
try:  #n and numshapes check
  n = abs(int(n)); numShapes = abs(int(numShapes))
  if (n == 0) or (numShapes == 0):
    arcpy.AddMessage("No shapes created and/or points per shape is zero")
    sys.exit()
except:
  arcpy.AddMessage("Improper entry for number of features or points per feature")
  sys.exit()
#
# Extent check
#
L, R, B, T = py_gp.gp_extent(arcpy)  # get the extent if any
#
# output check
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
  if (circCent == "random"):
    if numShapes > 1: 
      Xcent = random.uniform(L,R); Ycent = random.uniform(B,T)
    else:
      Xcent = L + ((R-L)/2.0); Ycent = B + ((T-B)/2.0)
  #
  #generate the points
  if theType == "Random":
    pnts = PM.circle_on(n, Xcent, Ycent, radius, "True") #random on
  elif theType == "Within":
    pnts = PM.circle_in(n, Xcent, Ycent, radius )    #random within
  else:
    pnts = PM.circle_on(n, Xcent, Ycent, radius, "False") #sequential on
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
  
  
