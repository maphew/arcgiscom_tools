'''py_gp_methods.py

Purpose:  methods specific to ArcGIS functionality are contained here

Authors
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created      May  2009
Last update  June 2013

Requires:  os, sys, string, Py_Points
           ArcGIS license to access the geoprocessor (arcpy)

Notes:
  Updated for version 10.x of ArcMap


'''
#imports
import os, sys, string
from Py_Points import *

#Methods
def createPointFile (outFC, outType, SR, pnts, fieldsToAdd, arcpy):
  '''Requires
    outFC     output feature class name "c:/temp/myfile.shp"
    outType   output type e.g. "Point"
    SR        Spatial reference from input feature class
    pnts      a list of lists of points eg.
              [[pnt list 1],[pnt list 2]...[pnt list n]]
          or  [[pnt list 1]]
    arcpy           the Geoprocessor Object
  Create the output filename and feature class, use the Spatial Reference
    of the input feature class
  '''
  import os, sys    #required if used in other modules
  fullName = os.path.split(outFC)
  outFolder = fullName[0].replace("\\","/")
  outFName =  fullName[1].replace(" ", "_")
  outFullName = outFolder + "/" + outFName
  try:
    arcpy.CreateFeatureclass_management(outFolder, outFName, outType, "#", "Disabled", "Disabled", SR)
    arcpy.AddMessage( "\n" + "Creating " + str(outFName))
  except:
    arcpy.AddMessage( "Failed to create feature class" + arcpy.GetMessages())
    sys.exit()
  for aField in fieldsToAdd:
    arcpy.AddMessage("Adding field " + str(aField))
    try:
      arcpy.AddField_management(outFullName, str(aField[0]), aField[1], aField[2], aField[3])
    except:
      arcpy.AddMessage("Failed to add fields: " + arcpy.GetMessages())
      sys.exit()
  #
  #Create the insert cursor
  aPnt = arcpy.CreateObject('point')
  try:
    cur = arcpy.InsertCursor(outFC)
  except:
    arcpy.AddMessage("failed to create cursor")
    sys.exit()
  anID=0
  for i in range(0,len(pnts)):    
    aList = pnts[i]
    aCount = 0
    for j in range(len(aList)):
      try:
        aPnt.X = aList[j].x 
        aPnt.Y = aList[j].y 
        aPnt.ID = aCount
        feat = cur.newRow()
        feat.Shape = aPnt
        feat.setValue("ID", aCount)
        feat.setValue("Group", anID)
        feat.setValue("X", aPnt.X)  #comment out if X and Y not needed
        feat.setValue("Y", aPnt.Y)
        cur.insertRow(feat)
        aCount = aCount + 1
      except:
        arcpy.AddMessage("cannot create feature", arcpy.GetMessages())
    anID = anID + 1
  del cur

def createPolyFile(outFC, outType, SR, pnts, theFields, gp):
  '''Requires
     outFC        output feature class name "c:/temp/myfile.shp"
     outType      output type "Polygon" or "Polyline" or "Polyline_closed"
     SR           Spatial reference from input feature class, otherwise "#"
     pnts         a list of lists of points
                   eg [ [10,10], [12,15], [7,3] ]
     theFields    the fields to add and their format
     arcpy        the Geoprocessor Object
  Create the output filename and feature class, use the Spatial Reference
    of the input feature class otherwise "#"
  '''

  import os, sys    #required if used in other modules 
  fullName = os.path.split(outFC)
  outFolder = fullName[0].replace("\\","/")
  outFName =  fullName[1].replace(" ", "_")
  outFullName = (outFolder + "/" + outFName)
  try:
    arcpy.CreateFeatureclass_management(outFolder, outFName, outType, "#", "Disabled", "Disabled", SR)
    gp.AddMessage("\n" + "Creating " + str(outFullName))
  except:
    arcpy.AddMessage("Failed to create feature class" + arcpy.GetMessages())
    sys.exit()
  #
  #Add any required fields fields
  if len(theFields) != 0:
    for i in range(0, len(theFields)):
      aField = theFields[i]
      try:
        arcpy.AddField_management(outFullName, aField[0], aField[1], aField[2], aField[3])
      except:
        arcpy.AddMessage("Cannot add field " + str(aField[0])+ "\n" + arcpy.GetMessages())
  try:
    cur = arcpy.InsertCursor(outFC)
  except:
    arcpy.AddMessage("failed to create cursor")
    del arcpy
    sys.exit()
  polyArray = arcpy.CreateObject("Array")
  aPnt = arcpy.CreateObject("Point")
  aCount = 0
  anID=0
  for i in range(0,len(pnts)):    
    aList = pnts[i]
    for j in range(len(aList)):
      try:
        aPnt.x = aList[j].x 
        aPnt.y = aList[j].y 
        polyArray.add(aPnt)
      except:
        arcpy.AddMessage("cannot create feature" + arcpy.GetMessages())
    if outType == "Polyline_closed":
      polyArray.add(polyArray.GetObject(0))
    feat = cur.newRow()
    feat.shape = polyArray
    feat.id = anID
    feat.setValue("ID", aCount)
    feat.setValue("Group", anID)
    cur.insertRow(feat)
    polyArray.removeAll()
    aCount = aCount + 1
    anID = anID+1
  del polyArray
  del aPnt
 
def gp_extent(arcpy):
  '''geoprocessor object required: returns L R B T'''
  extent = arcpy.Extent
  try:
    extList = string.split(str(extent), " ")
    for i in range(len(extList)):
      extList[i] = float(extList[i])
    L, B, R, T = extList
  except:  #no extent detected
    aMsg = "Extent set to L = 0; R = 100; T = 100; B = 0 " + \
           "since none was specified"
    arcpy.AddMessage(aMsg)
    L = 0; R = 100; T = 100; B = 0
  return [L, R, B, T]

def print_pnts(outPnts, arcpy):
  '''print a list of lists of points to gp output'''
  shapeNum = 0
  aLine = "%25s, %25s, %10s, %10s" % ("X", "Y", "ID", "Group")
  arcpy.AddMessage( aLine )
  for pnts in outPnts:
    aCount = 0
    for pnt in pnts:
      aLine = "%25.16f, %25.16f, %10i, %10i" \
              % (pnt.x, pnt.y, aCount, shapeNum)
      arcpy.AddMessage(aLine)
      aCount += 1
    shapeNum += 1

def print_msgs(msgs):
  for message in msgs:
    print message
    arcpy.AddMessage(message)

def shapeToPoints(a_shape,theType,arcpy):
  '''
  pnts = shapeToPoints(a_shape, shape type, geoprocessor)
  Purpose:  Converts a shape to points, the shape and its type
  are passed by the calling script
  Requires:  def pntXY(pnt)
  '''
  outList=[]
  part_num = 0
  part_count = a_shape.partCount
  if theType == "Multipoint":    #Multipoints
    while part_num < part_count:
      pnt = a_shape.getPart(part_num)
      XY = pntXY(pnt)
      if XY not in outList:
        outList.append(XY)
      part_num += 1
  else:                          #Poly* features
    while part_num < part_count: #cycle through the parts
      a_part = a_shape.getPart(part_num)
      pnt = a_part.next()
      while pnt:                 #cycle through the points
        XY = pntXY(pnt)
        if XY not in outList:
          outList.append(XY)
        pnt = a_part.next()      
        if not pnt:              #null point check (rings/donuts)
          pnt = a_part.next()
          if pnt:
            XY = pntXY(pnt)
            if XY not in outList:
              outList.append(XY)
      part_num += 1
  return outList

#--------------------------------------------------------------------
if __name__ == "__main__":
  print "hello"
