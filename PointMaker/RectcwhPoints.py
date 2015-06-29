'''
RectcwhPoints.py

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

  rect_ext    on the line

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
x_c = sys.argv[1]            #center x
y_c = sys.argv[2]            #center y
width = sys.argv[3]          #width
height = sys.argv[4]         #height
n  = sys.argv[5]             #number of points
outFC = sys.argv[6]          #output shapefile
outCSV = sys.argv[7]         #output csv file
outToScreen = sys.argv[8]    #output results to screen
#
#checks
#
#center check
try:
  x_c = float(x_c);  y_c = float(y_c)
except:
  arcpy.AddMessage("Center point is incorrect")
  sys.exit
#
#width height check
#
wh_msg = "Width and height must be > 0"
try:
  assert (width > 0) and (height > 0), wh_msg
  width = float(width);  height = float(height)
except:
  arcpy.AddMessage(wh_msg)
  sys.exit()
#
#size check
#
extMsg = "number of points must be > 0"
try:
  n = (int(n))
  if n < 0:
    arcpy.AddMessage(extMsg)
    sys.exit()
except:
  arcpy.AddMessage(extMsg)
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
#
pnts = PM.rect_cwh(n, x_c, y_c, width, height)
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
  
  
