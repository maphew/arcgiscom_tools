'''
GridPoints.py

Authors
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug 18, 2008
Updates  June 2013

Requires:  random, math, py_gp_methods, PointMaker

Notes:
  function  points

  grid_ext  points on a grid pattern
'''

#-----------------------------------------------------------------------------
#Main
#
import os, sys, string, math
import PointMaker as PM
#
import py_gp_methods as py_gp
import arcpy
#
arcpy.overwriteOutput = True
#
#inputs
arcpy.Extent = sys.argv[1]      #output extent
Cols = sys.argv[2]           #columns
Rows = sys.argv[3]           #rows
outFC = sys.argv[4]          #output shapefile
outCSV = sys.argv[5]         #output csv file
outToScreen = sys.argv[6]    #output results to screen
#
#checks
#
#  Extent check
#
L, R, B, T = py_gp.gp_extent(arcpy)  # get the extent if any
#
#row column check
#
extMsg = "Columns and Rows must be > 1"
try:
  Cols = abs(int(Cols));  Rows = abs(int(Rows))
  assert (Cols > 1) and (Rows > 1), extMsg
except:
  arcpy.AddMessage(extMsg)
  sys.exit()
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
#generate the points
#
pnts = PM.grid_ext(L, R, B, T, Cols, Rows)
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
  
  
