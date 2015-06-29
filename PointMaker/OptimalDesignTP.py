#OptimalDesignTP.py


#-----------------------------------------------------------------------------
#Main
#
import os, sys, string, math
#from PointClass import listToPoints
import Py_Points as PM
import GeneratePointsHelper as GPH
import GroupPntsHelper
import OptDesignHelper
#
import py_gp_methods as py_gp
import arcpy
#
arcpy.overwriteOutput = True
#
inFC = sys.argv[1]
groupField = sys.argv[2]   # to group by field
outFC = sys.argv[3].replace("\\","/")
outCSV = sys.argv[4]
MaxIter = sys.argv[5]
Threshold = sys.argv[6]
#
fullName = os.path.split(outFC)
outFolder = fullName[0].replace("\\", "/")
#
#Checks
#
# input must be point file
desc = gp.Describe
shapeClass = desc(inFC).ShapeType
if shapeClass != "Point":
  gp.AddMessage("\n" + "Requires a point file...bailing" + "\n")
  sys.exit()
else:
  gp.AddMessage("\n" + "Processing " + inFC )
#
#Maxiter and threshold check
try:
  MaxIter = abs(float(MaxIter))
  Threshold = abs(float(Threshold))
except:
  gp.AddMessage("Iterations or threshold values incorrect")
  sys.exit()
#
#filepath check
if outFC != "#":
  if not os.path.exists(outFolder):
    error = "Invalid path! Navigate to a folder and specify a filename.  " + \
            "Bailing..."
    gp.AddMessage("\n" + error + "\n")
    sys.exit()
#
#output check
if (outFC == "#") and (outCSV == "#"):
  outToScreen = "true"
  aMsg = "\n" + "No shapefile or csv file created..." + \
         "so output is directed to screen"
  gp.AddMessage(aMsg)
#
#End checks
#
#Get the geometry and OID fields and spatial reference
#
theType = desc(inFC).ShapeType
shapeField = desc(inFC).ShapeFieldName
OIDField = desc(inFC).OIDFieldName
fc = desc(inFC).CatalogPath.replace("\\","/")
SR = gp.CreateSpatialReference_management("#",fc,"#","#","#","#")
#
#Create output filename and output type
#
fullName = os.path.split(outFC)
outFolder = fullName[0].replace("\\", "/")
outType = "Point"
#
#Determine the grouping field type
#
gp.AddMessage("Grouping by: " + groupField)
if groupField != "#":
  fields = gp.ListFields(inFC)
  field = fields.next()
  while field:
    if field.Name == groupField:
      inType = field.Type
      if inType == "String":
        inPrec = "#"
        inScale = "#"
        inWidth = str(field.Length)
      elif inType in ["SmallInteger", "Integer", "Single", "Long", "OID"]:
        inPrec = str(field.Precision)
        inScale = "#"
        inWidth = "#"
      else:
        gp.AddMessage("\n" + "This field type... " + str(inType) + \
                      " ...is not supported for grouping, " + \
                      "use a text or integer field." + "\n")
        sys.exit()
    field = fields.next()
else:
  inType = "AllPoints"
  inPrec = "#"
  inScale = "#"
  inWidth = "6"
#
#perform a query to limit the points
#Create a SearchCursor and collect the points
#
rows = gp.SearchCursor(inFC)
rows.Reset()
row = rows.Next()
#
valueList = []
outPnts = []
gp.AddMessage("\n" + "Processing features")
#
if groupField == "#":   #collect points
  aVal = "None"
  pntList = []
  while row:
    aShape = row.Shape
    pnt = aShape.GetPart()
    vals = [pnt.X, pnt.Y, row.GetValue(OIDField)] #, aVal]
    pntList.append(vals)
    row = rows.next()
  #
  #Do the work
  #
  theReturned = OptDesignHelper.standardizePnts(pntList)
  pnts = theReturned[0]
  #pnts = pntList  #don't standardize the points
  ndx, mq, M, optimalDesign, nIter, TimeMQ = OptDesignHelper.OptDesign(pnts, 2, MaxIter, Threshold)
  #
  gp.AddMessage("\n" + "Support points " + str(ndx[0:mq]))
  gp.AddMessage("\n" + "MABE matrix " + str(M))
  #gp.AddMessage("\n" + "Weights " + str(optimalDesign))
  gp.AddMessage("\n" + "Iterations " + str(nIter))
  #
  supportMABE = OptDesignHelper.supportPnts(pntList, ndx[0:mq])
  #
  outPnts.append(supportMABE) #, "None"])
  #
else:                         #do points by groups
  theReturned = GroupPntsHelper.groupPoints(groupField, inFC, gp)
  pntList = theReturned[0]
  fldInfo = theReturned[1]
  valueList = theReturned[2]
  #
  #standardize the points
  #pntsStand = []
  #for i in pntList:
  #  theReturned = OptDesignHelper.standardizePnts(i)
  #  pntsStand.append(theReturned[0])
  #
  pntsStand = pntList #don't standardize the points
  #
  for i in range(len(pntsStand)):
    subPnts = pntsStand[i]
    theReturned = OptDesignHelper.OptDesign(subPnts, 2, MaxIter, Threshold)
    ndx, mq, M, optimalDesign, nIter, TimeMQ = theReturned
    #
    gp.AddMessage("\n" + "optimization results ndx, mq, M, OptDesign, nIter")
    varList = ["ndx : ", "mq", "M", "optDesign", "nIter"]
    for j in range(len(theReturned)):
      gp.AddMessage(str(varList[j]))
      gp.AddMessage(str(theReturned[j]))
    #Get the points from the original grouped points    
    supportMABE = OptDesignHelper.supportPnts(pntList[i], ndx[0:mq])
    gp.AddMessage("\n" + "support points " + str(supportMABE))
    outPnts.append(supportMABE) #, aVal])
    #

##gp.AddMessage("Iter, mq, Time ")
##for i in TimeMQ:
##  gp.AddMessage(str(i[0]) + ", " + str(i[1]) + ", " + str(i[2]))
#
if outFC != "#":
  fieldsToAdd = [["Group", "LONG", "9", "#", "#"]]

  gp.AddMessage("here" + str(outPnts))
  py_gp.createPointFile (outFC, outType, "#", outPnts, fieldsToAdd, gp)
  gp.AddMessage("\n" + "You can join the original table to " \
                + "this shapefile table if you want other attributes." + "\n")

if outCSV != "#":
  PM.to_CSV(outCSV, TimeMQ)
#-------------------------------------------------------------------------------
#five points which form an ellipse
#pnts = [[3.0,3.0],[6.0,9.0],[12.0,10.0],[15.0,5.0], [13.0,2.5]]  #five points
#
#those 5 points plus some inside the ellipse
#
#pnts = [[3.0,3.0],[3.1, 3.1],[4.0,4.0],[5.0,5.0],[6.0,9.0],[12.0,10.0],[13.0,2.5],[15.0,5.0]] 
#
#standardize the points
#
#theReturned = standardizePnts(pnts)
#pnts = theReturned[0]
#print"\n", "Standardized points"
#for i in pnts:
#  print i
#
#run optdesign
#
#ndx, mq, M, OptDesign, nIter = OptDesign(pnts, 2, 999, 0.00001)
#print "\n","Support points", ndx[0:mq] #-->Elements mq and beyond have been removed
#print "\nMABE approx", M
#print "\nWeights", OptDesign
#print "\nIterations", nIter
