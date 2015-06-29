'''
EllipseAnnulus.py

Author
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug 18, 2008
Updates  June 2013

Requires:  py_gp_methods, PointMaker

Notes:
  random is used to generate random numbers, check the random module
  in the Python documentation for more details.  A random
  floating point number between 0 and 1 is created.  If you want numbers
  within a specific range, then you can use uniform( a, b) where N is the
  number generated within the range defined by a and b.

  function  points created

  ell       between two ellipses with the same eccentricity
  ell_oval  ellipse eccentricities are different, thickness is constant
'''

#-----------------------------------------------------------------------------
#Main
#
import os, sys, string, math, random
import PointMaker as PM
import py_gp_methods as py_gp
import arcpy
#
arcpy.overwriteOutput = True
#
#inputs
theType = sys.argv[1]
ellCent = sys.argv[2]
major = sys.argv[3]
minor = sys.argv[4]
theta = sys.argv[5]
major2 = sys.argv[6]
n = sys.argv[7]              #number of points
numShapes = sys.argv[8]      #number of shapes to create
outFC = sys.argv[9]          #output shapefile
outCSV = sys.argv[10]
arcpy.Extent = sys.argv[11]     #output extent
outToScreen = sys.argv[12]   #output results to screen
#
#checks
#
try:  #center check
  aPair = string.split(ellCent," ")
  Xcent = float(aPair[0]); Ycent = float(aPair[1])
  arcpy.AddMessage("\n" + "Shapes centered at " + str(aPair))
  ellCent = "fixed"
except:
  arcpy.AddMessage("\n" + "Shapes centered randomly within dataframe extent")
  ellCent = "random"
#
try:  #axis check
  major = float(major); minor = float(minor)
  if (major == 0.0) or (minor == 0.0):  
    arcpy.AddMessage("A zero major or minor axis is not permitted")
    sys.exit()
  elif major < 0.0:
    arcpy.AddMessage("Random semi-major axis between 1 and 100 will be used")
    arcpy.AddMessage("semi-minor axis will be between 0.1 and 0.5 of the semi-major")
    arcpy.AddMessage("Inner semi-major axis will be 0.9 x outer semi-major")
    major = random.uniform(1, 100)
    minor = random.uniform(1,5)/10.0 * major
    major2 = major * 0.9
  else:
    arcpy.AddMessage("Ellipses will be " + str(major) + " " + str(minor))
except:
  arcpy.AddMessage("Invalid axis entry")
  sys.exit()
#
try:  #angle check
  theta = float(theta)
  ellAngle = "fixed"
  arcpy.AddMessage("Shapes created using rotation angle of " + str(theta))
except:
  ellAngle = "random"
  arcpy.AddMessage("Shapes created using random angles")
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
try:  #Inner major axis check
  major2 = float(major2)
  assert (major > major2 > minor), "Inner major axis is incorrect"
except:
    arcpy.AddMessage("Inner major axis is incorrect")
    sys.exit()
#
#output check
#
if (outFC == "#") and (outCSV == "#"):
  outToScreen = "true"
  aMsg = "\n" + "No shapefile or csv file created..." + \
         "so output is directed to screen"
  arcpy.AddMessage(aMsg)
#
#  Extent check
#
L, R, B, T = py_gp.gp_extent(arcpy)  # get the extent if any
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
#establish the center and axis orientations
outPnts = []
for i in range(numShapes):
  if (ellCent == "random"):
    if numShapes > 1: 
      Xcent = random.uniform(L,R); Ycent = random.uniform(B,T)
    else:
      Xcent = L + ((R-L)/2.0); Ycent = B + ((T-B)/2.0)
      arcpy.AddMessage("\n" + " centers(s) at... " + str(Xcent)+ " " + str(Ycent))
  if (ellAngle == "random"):
    theta = random.uniform(-180.0, 180.0)
  #
  #generate the points
  #
  arcpy.AddMessage("type " + str(theType))
  if theType == "Ellipse_annulus":
    pnts = PM.ellipse_annulus(n, Xcent, Ycent, theta, major, minor, major2)
  else:
    pnts = PM.ellipse_oval(n, Xcent, Ycent, theta, major, minor, major2)
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
  
  
