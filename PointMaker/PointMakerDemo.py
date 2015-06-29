'''
PointMakerDemo.py


  A sample shell program to generate ellipse point or polygon patterns.
  Ensure that this script, and the required scripts listed below, are
  in the same folder.
  
Authors
  D.E. Patterson
  W.A. Huber

Created      Aug 2008
Last update  April 2010

Requires
  py_gp_methods, PointMaker (which requires Py_Points)
  
'''

#imports
from PointMaker import *
import py_gp_methods
#reload(py_gp_methods)   #uncomment if py_gp_methods is edited
import random
#
#Create the geoprocessor and the shapefile
#  create an output shapefile for testing, change to suit

outFC = "c:/temp/test_shapefile2.shp"
  
gp, gp_version = py_gp_methods.gp_create()   #gp and version
print "Created using ArcGIS " + str(gp_version)
gp.OverWriteOutput = 1                       #overwrite existing files
fieldsToAdd = [["Group", "LONG", "9", "#", "#"]]

#  create n random ellipses using ellipse_on in PointMaker
#  set rand variable to False if creating polygons (createPolyFile)
#
outPnts = []
n = random.randint(1,100)           # between 1 and 100 random ellipses
for i in range(n):
  x_c = random.uniform(0,100)        # center x and y
  y_c = random.uniform(0,100)
  theta = random.uniform(-180, 180)  # rotation angle
  a = random.uniform(1,5)            # semi-major axis
  b = random.random() * a            # semi-minor axis
  rand = False                       # sequential points on an ellipse
  #
  pnts = ellipse_on(360, x_c, y_c, theta, a, b, rand)
  #
  outPnts.append( pnts )
#
#uncomment one of the four below
#  which demonstrate point, polygon, polyline and closed-loop polyline options

#py_gp_methods.createPointFile (outFC, "Point", "#", outPnts, fieldsToAdd, gp)
py_gp_methods.createPolyFile (outFC, "Polygon", "#", outPnts, fieldsToAdd, gp)
#py_gp_methods.createPolyFile (outFC, "Polyline", "#", outPnts, fieldsToAdd, gp)
#py_gp_methods.createPolyFile (outFC, "Polyline_closed", "#", outPnts, fieldsToAdd, gp)
print gp.GetMessages()
#
#alternately to a *.csv file, uncomment
#aFile = "c:/temp/test_csv_file.csv"
#to_CSV(aFile, outPnts )
