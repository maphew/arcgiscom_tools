'''
Grid_rot.py

Author
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug 18, 2008
Updates  June 2013

Requires:  random, math, PointMaker

Notes:
  function  points

  grid_rot  points on a grid pattern with rotation

'''
#-----------------------------------------------------------------------------
#Main
#
import os, sys, string, math
import PointMaker as PM
import py_gp_methods as py_gp
import arcpy
#
arcpy.overwriteOutput = True
#
#inputs
x_c = sys.argv[1]            #center x
y_c = sys.argv[2]            #center y
rot_angle = sys.argv[3]      #rotation angle
Cols = sys.argv[4]           #columns
Rows = sys.argv[5]           #rows
dx = sys.argv[6]             #x spacing
dy = sys.argv[7]             #y spacing
outFC = sys.argv[8]          #output shapefile
outCSV = sys.argv[9]         #output csv file
outToScreen = sys.argv[10]   #output results to screen
#
#checks
#
#  center check
try:
  x_c = float(x_c);  y_c = float(y_c)
except:
  arcpy.AddMessage("Center point is incorrect")
  sys.exit
#
#  rotation check
try:
  rot_angle = float(rot_angle)
except:
  arcpy.AddMessage("Rotation angle is incorrect")
  sys.exit()
#
#  row column check
#
extMsg = "Columns and Rows must be > 1"
try:
  Cols = abs(int(Cols));  Rows = abs(int(Rows))
  assert (Cols > 1) and (Rows > 1), extMsg
except:
  arcpy.AddMessage(extMsg)
  sys.exit()
#
#width height check
#
wh_msg = "x y spacing must be > 0"
try:
  assert (dx > 0) and (dy > 0), wh_msg
  dx = float(dx); dy = float(dy)
except:
  arcpy.AddMessage(wh_msg)
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
pnts = PM.grid_rot(x_c, y_c, rot_angle, Cols, Rows, dx, dy)
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
  
  
