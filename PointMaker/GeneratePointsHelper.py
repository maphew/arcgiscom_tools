'''GeneratePointsHelper.py

Author
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created  Aug 18, 2008
Updates  Sept 2013

Requires:  random, math

Notes:
  Random is used to generate random numbers, check the random module
  in the Python documentation for more details.  A random
  floating point number between 0 and 1 is created.  If you want numbers
  within a specific range, then you can use uniform( a, b) where N is the
  number generated within the range defined by a and b.

  function  points created

  onUC      on the circumference of the unit circle
  inUC      within the unit circle
  inAnn     with an annulus 
  binomial  uses binomial distribution
  onLine    on a line
  inELL     on an ellipse
'''

import os, sys, math, random

def onUC(n, radius, Xcent, Ycent ):
  '''n (no. points), radius, Xcent,Ycent (center point)
  random points on unit circle
  Bills notes:
    Most of the time, the unit circle will be the MABE,
    exception, when all points lie with a strip of width
    less than 1 (large chance for small n, chance decreases
    exponentially with large n.
  '''
  twoPI = math.pi*2.0
  pnts = []
  if radius < 0:
    radius = random.uniform(1,100)
  for i in range(n):
    t = random.random() * twoPI
    x = math.cos(t)*radius + Xcent;  y = math.sin(t)*radius + Ycent
    pnts.append([x,y])
  return pnts


def inUC(n, radius, Xcent, Ycent):
  '''n (no. points), radius, Xcent,Ycent (center point)
  uniform points within unit circle
  Bills notes:
    for sufficiently large n, the MABE will closely
    approximate the unit circle and the area will be
    close to pi.  Almost every MABE will have 5 support
    points
  '''
  twoPI = math.pi*2.0
  pnts = []
  for i in range(n):
    t = random.random() * twoPI
    r = radius * math.sqrt(random.random())
    x = r * math.cos(t) + Xcent;  y = r * math.sin(t) + Ycent
    pnts.append([x,y])
  return pnts

def inAnn(n, r1, r2, Xcent, Ycent):
  '''n (no. points), inner and outer radii, Xcent,Ycent (center point)
  uniform points within annulus
  Bills notes:
    for sufficiently large n, the MABE will closely
    approximate the unit circle and the area will be
    close to pi.  Almost every MABE will have 5 support
    points
  '''
  twoPI = math.pi*2.0
  pnts = []
  for i in range(n):
    t = random.random() * twoPI
    r = random.uniform(r1,r2)
    x = r * math.cos(t) + Xcent;  y = r * math.sin(t) + Ycent
    pnts.append([x,y])
  return pnts

def binormal(n, Xcent, Ycent, Xstd, Ystd, Rho):
  '''n (no. points), Xcent,Ycent (center point), Xstd, Ystd (stand dev), Rho (corr coeff)
  points by binormal distribution (bivariate normal)
  '''
  twoPI = math.pi*2.0
  pnts = []
  for i in range(n):
    t = 1.0 - random.random() * twoPI  #to ensure 0.0 is omitted 
    r = math.sqrt(-2.0 * math.log(1.0 - random.random()))
    x = math.cos(t)
    z = math.sin(t)
    y = Rho * x + math.sqrt((1 - Rho) * (1 + Rho)) * z
    x = Xcent + (Xstd * r * x)
    y = Ycent + (Ystd * r * y)
    pnts.append([x,y])
  return pnts


def onLine(n, length, u, v):
  '''n (no. of points), length, u, v (start and end points)
  generates random points along a line, the start and end
  points will be maintained
  '''
  twoPI = math.pi*2.0
  pnts = []
  t = random.random() * math.pi     #no factor of 2
  c = math.cos(t); s = math.sin(t)  #line slope
  pnts.append( [u - (length/2.0 * c), v - (length/2.0 * s)] ) # start
  pnts.append( [u + (length/2.0 * c), v + (length/2.0 * s)] ) # end
  halfLength = length/2.0
  for i in range(n-2):
    L = random.uniform(-halfLength,halfLength)  #random floating point
    x = L * c + u; y = L * s + v
    #x = (length * c) + u;  y = (length * s) + v
    pnts.append([x,y])
  return pnts

def onEll(n, a, b, theta, Xcent, Ycent):
  '''n (no. points), a, b (semi-major and minor axis, theta (rotation angle),
     Xcent,Ycent (center point)
  random points on ellipse
  Dans notes:
    Make an on-circle then scale and rotate it
  '''
  twoPI = math.pi*2.0
  theta = math.radians(theta)
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  pnts = onUC(n, a, 0.0, 0.0)  #UC centered at 0,0 with a radius 
  for i in range(len(pnts)):
    x = pnts[i][0]; y = pnts[i][1]
    t = math.atan2(y, x)
    a_cosQ = a * math.cos(t)
    b_sinQ = b * math.sin(t)
    x = cosT * a_cosQ - sinT * b_sinQ + Xcent
    y = sinT * a_cosQ + cosT * b_sinQ + Ycent
    pnts[i] = [x,y]
  return pnts

def inEll(n, a, b, theta, Xcent, Ycent):
  '''n (no. points), a, b (semi-major and minor axis, theta (rotation angle),
     Xcent,Ycent (center point)
  Dans notes:
    Make a within-circle then scale and rotate it
  '''    
  twoPI = math.pi*2.0
  theta = math.radians(theta)
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  pnts = inUC(n, a, 0.0, 0.0)  #points within UC with radius a
  fact = math.sqrt((b*b)/(a*a))
  for i in range(len(pnts)):
    dx = pnts[i][0]
    dy = pnts[i][1] * fact
    dist = math.hypot(dx, dy)
    t = math.atan2(dy, dx)
    cosQ = dist * math.cos(t)
    sinQ = dist * math.sin(t)
    x = cosT * cosQ - sinT * sinQ + Xcent
    y = sinT * cosQ + cosT * sinQ + Ycent
    pnts[i] = [x,y]
  return pnts
#-----------------------------------------------------------------------------
def createPointFile (outFC, outType, SR, pnts, fieldsToAdd, gp):
  '''Requires
    outFC        output feature class name "c:/temp/myfile.shp"
    outType      output theType "Polyline"
    SR           Spatial reference from input feature class
    polylines    a list of polylines (x,y,ID)
                  eg [ [10,10,1], [12,15,2], [7,3,3] ]
    gp           the Geoprocessor Object
  Create the output filename and feature class, use the Spatial Reference
    of the input feature class
  '''
  #import os, sys    #required if used in other modules
  fullName = os.path.split(outFC)
  outFolder = fullName[0].replace("\\","/")
  outFName =  fullName[1].replace(" ", "_")
  outFullName = outFolder + "/" + outFName
  try:
    gp.CreateFeatureclass_management(outFolder, outFName, outType, "#", "Disabled", "Disabled", SR)
    gp.AddMessage("\n" + "Creating " + str(outFName) + "\n")
  except:
    gp.AddMessage("Failed to create feature class" + gp.GetMessages())
    sys.exit()
  for aField in fieldsToAdd:
    gp.AddMessage("adding field " + str(aField))
    try:
      gp.AddField_management(outFullName, str(aField[0]), "LONG", "9")
    except:
      gp.AddMessage("Failed to add fields: " + gp.GetMessages())
      sys.exit()
  #
  #Create the insert cursor
  aPnt = gp.CreateObject('point')
  try:
    cur = gp.InsertCursor(outFC)
  except:
    gp.AddMessage("failed to create cursor")
    sys.exit()
  anID=0
  for i in range(0,len(pnts)):    
    aList = pnts[i]
    aCount = 0
    for j in range(len(aList)):
      try:
        aPnt.x = aList[j][0]
        aPnt.y = aList[j][1]
        aPnt.id = aCount
        feat = cur.NewRow()
        feat.shape = aPnt
        feat.SetValue("ID", aCount)
        feat.SetValue("Group", anID)
        cur.InsertRow(feat)
        aCount = aCount + 1
      except:
        gp.AddMessage("cannot create feature" + gp.GetMessages())
    anID = anID + 1
  del cur

def to_CSV(outCSV, outPnts, gp):   
  try:
    csvFile = open(outCSV,'w')
    csvFile.write("%25s %25s %10s %10s" % ("X", "Y", "ID", "Group"))
  except:
    gp.AddMessage("File opening error " + gp.GetMessages())
    sys.exit()
  #
  shapeNum = 0
  for pnts in outPnts:
    aCount = 0
    for pnt in pnts:
      x = "%25.16f" % (pnt[0]); y = "%25.16f" % (pnt[1])
      pntid = "%10i" % (aCount); shape = "%10i" % (shapeNum)
      aLine = "\n" + x + "," + y + "," + pntid + "," + shape
      csvFile.write(aLine)
      aCount += 1
    shapeNum += 1
  csvFile.flush()
  csvFile.close()

