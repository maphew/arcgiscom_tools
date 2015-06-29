'''
PointMaker.py

Create Point distributions

Author
  D.E. Patterson
  with a great deal of assistance from W.A. Huber

Created      Aug 2008
Last update  June 2013

Requires:  math, os, random, sys, Py_Points

Notes:
  Random numbers:
  The function random or uniform is used to generate random numbers.
  The random method generates floating point numbers between 0 and 1.
  If you want numbers within a specific range, then use
  uniform(a, b) where the number generated within the range defined
  by a and b.

  Points:
  Points are created using the Point class within the Py_Points module.

  Options:

  Function     Points created
  
  bool_test    none, checks for random options where applicable
  annulus      random points within an annulus
  binormal     random points using binormal distribution
  circle_in    random points on a circle
  circle_on    random/uniformly spaced points on a circle
  ellipse_annulus
               random points within an annulus, transformed back to an
               ellipse, spacing between ellipses is not constant
  ellipse_in   random points within an ellipse
  ellipse_on   random/uniformly spaced points on an ellipse
  ellipse_oval random points between an ellipse and an oval, spacing
               between features is constant
  ellipse_parallel
               
  grid_ext     uniformly spaced grid top-left to bottom-right
  grid_rot     grid with optional differential x,y spacing and rotation
  line_about   random/uniformly spaced points on/forming a line
               with random y-value pertubation about the line
  line_on      random/uniformly spaced points on/forming a line
  rect_cwh     random points within width and height around center
  rect_ext     random points within an extent
  to_csv       output to *.csv file format

  '''

#imports
import os, sys, math, random
from Py_Points import *

#constants
twoPI = math.pi*2.0

def bool_test(value):
  '''a hack since some programs will only allow strings to
     be passed as arguments rather than True/False booleans'''
  if value in [True, "True", "true", "T", "t"]:
    return True
  else:
    return False
  
def annulus(n=10, x_c=0, y_c=0, inner=0.5, outer=1.0 ):
  '''in annulus: n random points, center, inner/outer radii'''
  assert (outer > inner) and (outer > 0) and (inner > 0), \
         "Annulus error, ensure outer > inner > 0" 
  pnts = []
  for i in range(n):
    theta = random.random() * twoPI
    r = random.uniform(inner, outer)
    x = r * math.cos(theta) + x_c
    y = r * math.sin(theta) + y_c
    pnts.append(Point(x,y))
  return pnts

def binormal(n=10, x_c=0, y_c=0, s_x=1, s_y=1, rho=0):
  '''binormal distribution: center, std devs, correl coeff'''
  assert (rho >= -1.0) and (rho <= 1.0), \
         "Binormal error:  -1 <= rho <= 1.0"
  assert (s_x >= 0.0) and (s_y >= 0.0), \
         "Binormal error:  std deviations > 0.0 required"
  pnts = []
  rhoPrime = math.sqrt((1 - rho) * (1 + rho))
  for i in range(n):
    theta = random.random() * twoPI
    r = math.sqrt(-2.0 * math.log(1.0 - random.random()))
    cosT = math.cos(theta)
    sinT = math.sin(theta)
    y = rho * cosT + rhoPrime * sinT
    x = x_c + s_x * r * cosT
    y = y_c + s_y * r * y
    pnts.append(Point(x,y))
  return pnts

def circle_in(n=10, x_c=0, y_c=0, radius=1):
  '''in circle: n random points, center and radius'''
  assert radius > 0, "Circle error:  set radius > 0"
  pnts = []
  for i in range(n):
    t = random.random() * twoPI
    r = radius * math.sqrt(random.random())
    x = r * math.cos(t) + x_c
    y = r * math.sin(t) + y_c
    pnts.append(Point(x,y))
  return pnts

def circle_on(n=10, x_c=0, y_c=0, radius=1, rand=True):
  '''on circle: n random/uniform points, center, radius, random T/F'''
  assert radius > 0, "Circle error:  set radius > 0"
  rand = bool_test(rand)
  pnts = []
  step = math.radians(360.0/n) #step for uniform
  start = math.radians(180.0)  #start for uniform
  for i in range(n):
    if rand:     #random points on circle
      t = random.random() * twoPI
    else:        #uniform points on circle
      t = start - (i * step)  #angle from 180 to -180
    x = math.cos(t)*radius + x_c
    y = math.sin(t)*radius + y_c
    pnts.append(Point(x,y))
  return pnts

def ellipse_annulus(n=10, x_c=0, y_c=0, theta=0, a=2, b=1, a_inner=1.8 ):
  '''elliptical annulus: n random points, center, angle, a b axes, inner a
     Make an annulus then scale and rotate it
     a, b are the semi-major and semi-minor axes of the outer ellipse.
     a_inner is the semi-major axis of the inner ellipse.
     Constant distance is not maintained around the ellipse, see
     ellipse_oval for that implementation
   '''
  assert (a > a_inner > b > 0), "Ellipse error:  set a > a_inner > b > 0"
  a = float(a);  b = float(b); a_inner = float(a_inner)
  theta = math.radians(theta)
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  #
  pnts = annulus(n, 0.0, 0.0, a_inner, a)  #points within UC with radius a
  #
  fact = math.sqrt((b*b)/(a*a))
  for i in range(len(pnts)):
    dx = pnts[i].x
    dy = pnts[i].y * fact
    dist = math.hypot(dx, dy) 
    t = math.atan2(dy, dx)
    cosQ = dist * math.cos(t)
    sinQ = dist * math.sin(t)
    x = cosT * cosQ - sinT * sinQ + x_c
    y = sinT * cosQ + cosT * sinQ + y_c
    pnts[i] = Point(x,y)
  return pnts

def ellipse_in(n=10, x_c=0, y_c=0, theta=0, a=2, b=1):
  '''in ellipse: n random points, center, angle, axes'''
  #  Make a within-circle then scale and rotate it
  assert (a > 0) and (b > 0) and (a >= b), \
         "Ellipse error:  set a >= b > 0"
  a = float(a);  b = float(b)
  theta = math.radians(theta)
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  #
  pnts = circle_in(n, 0.0, 0.0, a )  #points within UC with radius a
  #
  fact = math.sqrt((b*b)/(a*a))
  for i in range(len(pnts)):
    dx = pnts[i].x
    dy = pnts[i].y * fact
    dist = math.hypot(dx, dy)
    t = math.atan2(dy, dx)
    cosQ = dist * math.cos(t)
    sinQ = dist * math.sin(t)
    x = cosT * cosQ - sinT * sinQ + x_c
    y = sinT * cosQ + cosT * sinQ + y_c
    pnts[i] = Point(x,y)
  return pnts

def ellipse_on(n=10, x_c=0, y_c=0, theta=0, a=2, b=1, rand=True):
  '''on ellipse: n random/uniform points, angle, center axes, random T/F'''
  #  Make a on-circle then scale, rotate and translate
  assert (a > 0) and (b > 0) and (a >= b), \
         "Ellipse error:  set a >= b > 0"
  rand = bool_test(rand)
  theta = math.radians(theta)
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  #
  if rand:
    pnts = circle_on(n, 0.0, 0.0, a, True)  #circle centered at 0,0 with a radius 
  else:
    pnts = circle_on(n, 0.0, 0.0, a, False)
  #
  for i in range(len(pnts)):
    x = pnts[i].x; y = pnts[i].y
    t = math.atan2(y, x)
    a_cosQ = a * math.cos(t)
    b_sinQ = b * math.sin(t)
    x = cosT * a_cosQ - sinT * b_sinQ + x_c
    y = sinT * a_cosQ + cosT * b_sinQ + y_c
    pnt = Point(x,y)
    pnt.theta = t   #store the angle with the point
    pnts[i] = pnt
  return pnts

def ellipse_oval(n=10, x_c=0, y_c=0, theta=0, a=2, b=1, thickness=0.2):
  '''elliptical annulus: n random points, center, angle, a b axes, thickness'''
  assert (a > b > 0), "Ellipse error:  set a > b > 0"
  a = float(a);  b = float(b);  thickness = float(thickness)
  pnts = []
  for i in range(n):
    t = random.random() * twoPI
    c = math.cos(t); s = math.sin(t)
    angle = math.atan2(s,c)
    d = random.uniform(0, thickness)
    x = a * c + d * math.cos(angle)
    y = b * s + d * math.sin(angle)
    pnt = Point(x,y)
    pnt = pnt.rotate(theta)
    pnt = pnt.move(x_c, y_c)
    pnts.append(pnt)
  return pnts

def ellipse_parallel(n=10, x_c=0, y_c=0, theta=0, a=2, b=1, thickness=0.2):
  '''parallel to ellipse: n sequential points, center, angle, a b axes, thickness'''
  assert (a > b > 0), "Ellipse error:  set a > b > 0"
  a = float(a);  b = float(b);  thickness = float(thickness)
  pnts = ellipse_on(n, 0.0, 0.0, 0.0, a, b, rand=False)
  for i in range(len(pnts)):
    p = pnts[i]
    t = p.theta    #point angle stored with point in ellipse_on
    c = math.cos(t); s = math.sin(t)
    angle = math.atan2(s,c)
    denom = math.sqrt(b*b * c*c + a*a * s*s)
    x1 = p.x; y1 = p.y
    if denom != 0.0:
      x = (thickness / denom) * b * c + x1
      y = (thickness / denom) * a * s + y1
    pnt = Point(x,y)
    pnt = pnt.rotate(theta)
    pnt = pnt.move(x_c, y_c)
    pnts[i] = pnt
  return pnts

def grid_ext(L=-5.0, R=5.0, B=-5.0, T=5.0, cols=10, rows=10):
  '''grid pattern, by rows and cols: within left, right, bottom, top, cols, rows'''
  assert (L < R) and (B < T), \
         "Grid_ext error: check your L, R, B, and T values"
  assert rows > 1 and cols > 1, \
         "Grid_ext error: cols and rows > 1"
  from decimal import Decimal
  pnts = []
  dx = Decimal(str(R - L)) / Decimal(str(cols - 1))
  dy = Decimal(str(T - B)) / Decimal(str(rows - 1))
  L = str(L)
  B = str(B)  #use for bottom to top
  #T = str(T) #use for top to bottom
  for r in range(rows):
    r = Decimal(str(r))
    for c in range(cols):
      c = Decimal(str(c))
      x = (Decimal(L) + Decimal(c) * dx)
      y = (Decimal(B) + Decimal(r) * dy)  #bottom to top
      #y = (Decimal(T) - Decimal(r) * dy)  #top to bottom
      pnts.append(Point(x,y))
  return pnts 

def grid_rot(x_c=0.0, y_c=0.0, theta=0.0, cols=10, rows=10, dx=1.0, dy=1.0):
  '''grid pattern, with rotation: center, angle, rows, cols, dx, dy'''
  assert (dx > 0) and (dy > 0), \
         "Grid_rot error: set dx and dy > 0"
  assert rows > 1 and cols > 1, \
         "Grid_rot error: cols and rows > 1"
  theta = math.radians(theta)
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  pnts = []
  x_s = (cols - 1) * dx / 2.0  #center the grid and set extent
  y_s = (rows - 1) * dy / 2.0
  L = -x_s; R = x_s
  B = -y_s; T = y_s
  for r in range(rows):
    for c in range(cols):
      x = L + c * dx           #create the grid points
      y = T - r * dy
      x1 = (x * cosT - y * sinT) + x_c  #rotate, translate
      y1 = (x * sinT + y * cosT) + y_c
      pnts.append(Point(x1,y1))
  return pnts 

def line_about(n=10, x_c=0, y_c=0, theta=0, leng=1, rand=True, jitter=0.1):
  '''on line: n random/uniform points, angle, center, length, jitter'''
  assert (leng > 0) and (jitter >= 0), \
         "Line_about error: set leng and jitter > 0"
  rand = bool_test(rand)
  pnts = []
  theta = math.radians(theta)
  start = -leng/2.0
  stop = leng/2.0
  step = (leng * 1.0)/n   #step for uniform
  if not rand:
    n = n + 1            #ensure start and end points are created
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  for i in range(n):
    dy = random.uniform(-jitter, jitter)   #scatter about the line
    if rand:
      L = random.uniform(start, stop) #(random.random())
    else:
      L = start + (i * step)
    if theta != 0.0:
      #x = (L * cosT) + x_c         #original
      #y = ((L + dy) * sinT) + y_c  #original
      x = (L * cosT - dy * sinT) + x_c  #rotate, translate
      y = (L * sinT + dy * cosT) + y_c
    else:
      x = L  + x_c
      y = dy + y_c
    pnts.append(Point(x,y))
  return pnts
  
def line_on(n=10, x_c=0, y_c=0, theta=0, leng=1, rand=True):
  '''on line: n random/uniform points, center, angle, length, random T/F'''
  assert (leng > 0), "Line_on error: set leng > 0"
  rand = bool_test(rand)
  pnts = []
  theta = math.radians(theta)
  start = -leng/2.0
  stop = leng/2.0
  step = (leng * 1.0)/n   #step for uniform
  if not rand:
    n = n + 1            #ensure start and end points are created
  cosT = math.cos(theta)
  sinT = math.sin(theta)
  for i in range(n):
    if rand:
      L = random.uniform(start, stop) #(random.random())
    else:
      L = start + (i * step)
    x = (L * cosT) + x_c
    y = (L * sinT) + y_c
    pnts.append(Point(x,y))
  return pnts

def rect_cwh(n=10, x_c=0.0, y_c=1.0, dx=1.0, dy=1.0):
  '''n random points in rectangle extent: center x-y, width, height'''
  pnts = []
  assert (dx > 0.0) and (dy > 0.0), \
         "Rect_cwh error: check your width and height"
  L = x_c - dx/2.0; R = x_c + dx/2.0
  B = y_c - dy/2.0; T = y_c + dy/2.0
  for i in range(n):
    x = L + dx * random.random()
    y = B + dy * random.random()
    pnts.append(Point(x,y))
  return pnts

def rect_ext(n=10, L=-1, R=1, B=-1, T=1):
  '''n random points in rectangle extent: left, right, bottom, top'''
  pnts = []
  assert (L < R) and (B < T), \
         "Rect_ext error: check your L, R, B, and T values"
  dx = (float(R) - float(L))
  dy = (float(T) - float(B))
  print dx, dy
  for i in range(n):
    x = L + dx * random.random()
    y = B + dy * random.random()
    pnts.append(Point(x,y))
  return pnts

def to_CSV(outCSV, outPnts):
  '''output location and filename, output points'''
  try:
    csvFile = open(outCSV,'w')
    csvFile.write("%10s, %10s, %25s, %25s, %10s" % \
                  ("FID", "ID", "X", "Y", "Group"))
  except:
    print "File opening error "
    sys.exit()
  #
  pnt_num = 0
  shapeNum = 0
  for pnts in outPnts:
    aCount = 0
    for pnt in pnts:
      FID = "%10i" % (pnt_num)
      x = "%25.16f" % (pnt.x)
      y = "%25.16f" % (pnt.y)
      pnt_id = "%10i" % (aCount)
      shape = "%10i" % (shapeNum)
      aLine = "\n" + FID + ", " + pnt_id + ", " + x + ", "\
              + y + ", " + shape
      csvFile.write(aLine)
      pnt_num += 1
      aCount += 1
    shapeNum += 1
  csvFile.flush()
  csvFile.close()


#----------------------------------------------------------
if __name__ == "__main__":
  print "\n", "PointMaker.py is loaded"
  #
  #create an output *.csv file for testing, change to suit
  aFile = "c:/temp/test.csv"
  #
##  inA = annulus(100, -5.0, 15.0, 1.5, 2.0)
##  print "\n", "in annulus: ", "\n", inA
##  
##  binorm = binormal(300, 0.0, 15.0, 1, 1, 0.8)
##  print "\n", "binormal: ", "\n", binorm
##
##  binorm2 = binormal(300, 5.0, 15.0, 0.5, 0.5, -0.5)
##  print "\n", "binormal 2: ", "\n", binorm2
##
##  binorm3 = binormal(300, 10.0, 15.0, 1, 1, 0)
##  print "\n", "binormal 3: ", "\n", binorm3  
##
##  randC = circle_on(20, -5.0, 10.0, 1.5, True)
##  print "\n", "random on circle: ", "\n", randC
##
##  uniC = circle_on(36, 0.0, 10.0, 1.5, False)
##  print "\n", "uniform on circle: ", "\n", uniC
##  
##  inC = circle_in(50, 5.0, 10.0, 1.5)
##  print "\n", "random in circle: ", "\n", inC
## 
##  onEll = ellipse_on(36, -5, 5, 30, 2, 1, True)
##  print "\n", "random on ellipse: ", "\n", onEll
##
##  onEllU = ellipse_on(36, 0, 5, 30, 2, 1, False)
##  print "\n", "uniform on ellipse: ", "\n", onEllU

##  inEll = ellipse_in(50, 5, 5, -30, 2, 1 )
##  print "\n", "random in ellipse: ", "\n", inEll
##  
##  ellAnn = ellipse_annulus(1000, 10, 5, 0, 2, 1, 1.8)
##  print "\n", "ellipse annulus: ", "\n", ellAnn
##  
##  ellOval = ellipse_oval(1000, 15, 5, 15, 2, 1, -0.2)
##  print "\n", "ellipse oval: ", "\n", ellOval
##  onEllU2 = ellipse_on(360, 15, 5, 15, 2, 1, False)    #bounding ellipses
##  onEllU3 = ellipse_on(360, 15, 5, 15, 1.8, 0.8, False)
##
##  onEllU4 = ellipse_on(360, 20, 5, 15, 2, 1, False)     #parallel ellipses
##  ellParall = ellipse_parallel(360, 20, 5, 15, 2, 1, 0.2)
  
  #inGrid = grid_ext(4, 8, -6, -2, 5, 5)
  inGrid = grid_ext(0, 100, 0, 100, 10, 10)
  print "\n", "grid pattern: ", "\n", inGrid

##  inGridrot = grid_rot(12, -4.0, 30.0, 20, 10, 0.25, 0.25)
##  print "\n", "grid pattern 2: ", "\n", inGridrot
##  
##  onL = line_on(50, -5, 0, 45, 5, True)
##  print "\n", "random on line: ", "\n", onL
##  
##  onLU = line_on(20, 0, 0, -30, 5, False)
##  print "\n", "uniform on line: ", "\n", onLU
##
##  aboutL = line_about(50, 5, 0, 30, 5, False, 0.1)
##  print "\n", "scatter on sequential line: ", "\n", aboutL
##
##  aboutL2 = line_about(1000, 50, 50, 30, 100, "True", 1.0)
##  print "\n", "scatter on line, random: ", "\n", aboutL2  
##  
##  inRect = rect_ext(100, -6.0, -2.0, -6.0, -2.0)
##  print "\n", "within rectangle: ", "\n", inRect
##
##  inRect2 = rect_cwh(100, 1.0, -4.0, 4.0, 4.0)
##  print "\n", "within rectangle, version 2: ", "\n", inRect2
  
  print "\n", "Writing points to: ", aFile
##  allPnts = [inA,
##             binorm, binorm2, binorm3,
##             randC, uniC, inC,
##             onEll, onEllU, inEll,
##             onL, onLU, aboutL, aboutL2,
##             inRect, inRect2,
##             inGrid, inGridrot,
##             ellAnn, ellOval, onEllU2, onEllU3, ellParall, onEllU4]
##  allPnts = [ellParall, onEllU2, onEllU3]
  allPnts = [inGrid]
  to_CSV(aFile, allPnts )

  
