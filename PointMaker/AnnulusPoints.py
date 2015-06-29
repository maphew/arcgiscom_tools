'''AnnulusPoints.py

Author
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug, 2008
Updates  June 2013

Requires:  random, math, py_gp_methods, PointMaker

Notes:
  random is used to generate random numbers, check the random module
  in the Python documentation for more details.  A random
  floating point number between 0 and 1 is created.  If you want numbers
  within a specific range, then you can use uniform( a, b) where N is the
  number generated within the range defined by a and b.

  function  points created within an annulus

'''
#-----------------------------------------------------------------------------
#Main
#
import os, sys, string, math, random
import PointMaker as PM
import py_gp_methods as py_gp
import arcpy
#
arcpy.overWriteOutput = True
#
#inputs
annCent = sys.argv[1]        #center
radius = sys.argv[2]         #major radius
radius2 = sys.argv[3]        #minor radius
n = int(sys.argv[4])         #number of points
numShapes = int(sys.argv[5]) #number of shapes to create
outFC = sys.argv[6]          #output shapefile
outCSV = sys.argv[7]         #output csv file
arcpy.Extent = sys.argv[8]      #output extent
outToScreen = sys.argv[9]    #output results to screen
#
#checks
#
try:  #center check
  aPair = string.split(annCent," ")
  Xcent = float(aPair[0]); Ycent = float(aPair[1])
  arcpy.AddMessage("\n" + "Shapes centered at " + str(aPair))
  annCent = "fixed"
except:
  arcpy.AddMessage("\n" + "Shapes centered randomly within dataframe extent")
  annCent = "random"
#
random_rad = False
try:  #radii checks
  radius = float(radius); radius2 = float(radius2)
  if (radius <= 0.0) or (radius2 <= 0.0):
    arcpy.AddMessage("Radii must be greater than zero.")
    sys.exit()
  elif (radius <= radius2):
    arcpy.AddMessage("Inner radius must be less than outer.")
    sys.exit()
  else:
    rad = str(radius) + " " + str(radius2)
    arcpy.AddMessage("Annulus will be created using radii of " + rad)
except:
  random_rad = True
  arcpy.AddMessage("Annulus will be created using random radii")
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
  if (annCent == "random"):
    if numShapes > 1: 
      Xcent = random.uniform(L,R); Ycent = random.uniform(B,T)
    else:
      Xcent = L + ((R-L)/2.0); Ycent = B + ((T-B)/2.0)
  if random_rad == True:
    rad_max = (R - L) * 0.1   #max is 10%  of width
    rad_min = (R - L) * 0.01  #min is 1% of width
    radius = random.uniform(rad_min, rad_max)
    radius2 = radius * random.uniform(0.5, 0.99)
  #
  #generate the points
  #
  pnts = PM.annulus(n, Xcent, Ycent, radius2, radius)
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
  
