'''
GroupPntsHelper.py
Author
  D.E. Patterson

Created  Aug, 2008
Updates  June 2013 
'''

def getPnts(rows):
  row = rows.next()
  pnts=[]
  while row:
    aShape = row.Shape
    pnt = aShape.GetPart()
    XY = [pnt.X, pnt.Y]    #get the X and Y
    if XY not in pnts:
      pnts.append(XY)
    row = rows.next()
  return pnts
#-----------------------------------------------------------------
def groupPoints(inField, inFC, gp):
  groupedPoints = []  # list to hold grouped points
  theFields = gp.ListFields(inFC)
  inType = ""
  desc = gp.Describe
  OIDField = desc(inFC).OIDFieldName
  OKFields = [OIDField]

  gp.AddMessage("\n" + "Possible grouping fields" + "\n" + \
                "%-10s %-10s %-6s %-6s %-6s %-6s " % \
                ("Field","Type","Prec","Scale","Length","Useable"))
  for aField in theFields:
    fType = aField.Type
    fScale = aField.Scale
    fName = aField.Name
    fPrec = aField.Precision
    fLeng = aField.Length
    if fName == inField:
      inName = fName
      inType = fType   #used to determine field type later on
      inPrec = fPrec
      inScale = fScale
      inLeng = fLeng
      inFieldInfo = [inName, inType, inPrec, inScale, inLeng]  #added May 2008
    isOK = "Y"
    if (fType == "String"):
      OKFields.append(fName)
    elif ((fScale == 0) and (fType !="Geometry")):
      OKFields.append(fName)
    else:
      isOK = "N"     
    gp.AddMessage("%-10s %-10s %-6s %-6s %-6s %-6s" % \
                  (fName, fType, fPrec, fScale, fLeng, isOK))

  #
  if inField not in OKFields:
    gp.AddMessage("The field " + inField + " is not an appropriate" + \
                  " field type.  Terminating operation." + "\n")  
    del gp
    sys.exit()
  #  
  #Determine unique values in the selected field
  gp.AddMessage(inField + " is being queried for unique values." + "\n")
  valueList = []
  rows = gp.SearchCursor(inFC)
  row = rows.next()
  aString = ""
  aLen = 0; aFac = 1
  while row:
    aVal = row.GetValue(inField)
    if aVal not in valueList:
      valueList.append(aVal)
      aLen = len(aString)
      if aLen > 50 * aFac:
        aString = aString + "\n"
        aFac = aFac + 1
      aString = aString + " " + str(aVal)
    row = rows.next()
  #gp.AddMessage("Unique values: " + "\n" + aString)
  #
  #Do the actual work of producing the unique shapefiles
  aMax = 1
  outVals = []  # a list to append valid output values
  for aVal in valueList:
    aMax = max(aMax,len(str(aVal)))
  for aVal in valueList:
    if (str(aVal).isdigit()) and (not inType == "String"):
      fs = '"'+"%"+str(aMax)+"."+str(aMax)+'i"'
      aSuffix = fs % aVal
      aVal = str(aVal)
    elif inType == "Double" and inScale == 0:
      aSuffix = str(aVal).replace(".0","")  ###### 
      aVal = str(aVal).replace(".0","")
    else:
      aSuffix = str(aVal) 
      aVal = str(aVal)
    try:
      #Create a query and produce the file
      if (not aVal.isdigit()) or (inType == "String"):
        aVal = "'"+aVal+"'"
      whereClause = "%s = %s" % (inField, aVal)
      TempLayer = "TempLayer"
      gp.MakeFeatureLayer_management(inFC, TempLayer, whereClause)
      #
      rowsNew = gp.SearchCursor("TempLayer")
      pnts = getPnts(rowsNew)
      if len(pnts) >= 3:   #need 3 valid points for a convex hull
        groupedPoints.append(pnts)
        outVals.append(aVal)
    except:
      gp.AddMessage("Could not create temporary layer" + "\n")
      whereClause = "%s = %s" % (inField, aVal)
  del rows
  del rowsNew
  TempLayer = None
  return [groupedPoints, inFieldInfo, outVals]
