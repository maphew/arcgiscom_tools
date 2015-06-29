'''
LinePoints.py

Authors
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

  function  points created

  onLine    on the line
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
theType = string.split(sys.argv[1]," ")[0]
lineSlope = sys.argv[2]
lineCent = sys.argv[3]
length = sys.argv[4]
n = sys.argv[5]              #number of points
scatter = sys.argv[6]
numShapes = sys.argv[7]      #number of shapes to create
outFC = sys.argv[8]          #output shapefile
outCSV = sys.argv[9]         #output csv file
arcpy.Extent = sys.argv[10]      #output extent
outToScreen = sys.argv[11]    #output results to screen
#
#checks
#
try:  #slope check
  lineSlope = float(lineSlope)
except:
  lineSlope = "random"
  arcpy.AddMessage("\n" + "Slopes selected randomly")
#
try:  #center check
  aPair = string.split(lineCent," ")
  Xcent = float(aPair[0]); Ycent = float(aPair[1])
  arcpy.AddMessage("\n" + "Shapes centered at " + str(Xcent) + ", " + str(Ycent))
  lineCent = "fixed"
except:
  arcpy.AddMessage("\n" + "Shapes centered randomly within dataframe extent")
  lineCent = "random"
#
try:  #length check
  length = float(length)
  if length == 0.0:
    arcpy.AddMessage("A zero length is not permitted")
    sys.exit()
  elif length < 0.0:
    arcpy.AddMessage("Random lengths between 1 and 100 will be used")
  else:
    arcpy.AddMessage("Lines will be created using a length of " + str(length))
except:
  arcpy.AddMessage("Invalid length entry")
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
#scatter check
try:
  scatter = float(scatter)
except:
  arcpy.AddMessage("Scatter must be >= 0")
  sys.exit()
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
outPnts = []
for i in range(numShapes):
  if lineSlope == "random":
    lineSlope_out = random.uniform(-180, 180)
  else:
    lineSlope_out = lineSlope
  if (lineCent == "random"):
    if numShapes > 1: 
      Xcent = random.uniform(L,R); Ycent = random.uniform(B,T)
    else:
      Xcent = L + ((R-L)/2.0); Ycent = B + ((T-B)/2.0)
  if (length < 0.0):
    length_out = random.uniform(1, 100)
  else:
    length_out = length
  #
  #generate the points
  #
  if scatter == 0.0:
    if theType == "Random":
      pnts = PM.line_on(n, Xcent, Ycent, lineSlope_out, length_out, "True")
    else:
      pnts = PM.line_on(n, Xcent, Ycent, lineSlope_out, length_out, "False")
  else:
    if theType == "Random":
      pnts = PM.line_about(n, Xcent, Ycent, lineSlope_out, length_out, "True", scatter)
    else:
      pnts = PM.line_about(n, Xcent, Ycent, lineSlope_out, length_out, "False", scatter)
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
