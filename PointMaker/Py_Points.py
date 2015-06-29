'''
Py_Points.py

  Name:  Py_Points

  Purpose:  Point and vector class, plus point and vector methods
  
  Author:  D.E. Patterson

  Created:  Sept, 2008

  Last Modification:  June 2013
  
  Source:  various point classes served as inspiration

  Useage:
    from Py_Points import *

  to ensure that the class and defs are imported
  using the same namespace or

  import Py_Points

  which will require that you use Py_Points.Point...
  methods of class/function access

  ---------------------------------------------------------
  Point class includes functions that:
  
  Create points
    __init__

  Print points
    __repr__

  Point math
    __add__,  __sub__,  __mul__,  __div__  +,-,*,/ functions
    __radd__, __rsub__, __rmul__, __rdiv__ right-sided versions
    __iadd__, __isub__, __imul__, __idiv__ in-place versions

  Get/set/modify points attributes
    setX, setY  set X,Y values
    getX, getY  get X,Y values

  Geometric operations
    move
    perpend
    rotate      
    scale
    translate

  Return values that use objects
    dist        calculate distance between 2 points

  ---------------------------------------------------------
  Vector class is for methods that use two points

  inherits from Point class, so all of the above apply
  
  Create vectors
    __init__  

  methods include:
    angle
    dot
    length
    project
    unit

  ---------------------------------------------------------

  Conversion
    to_point
    list_to_points
    points_to_list

  Statistical
    center
    center_extent
    extent
    get_xs_ys
    moments

  Sorting
    sort_lex
    sort_radial
    sort_dist

  Transformation
    standardize_pnts
    transform_back
  '''

#Required modules
import math

#Class definitions
'''Point   2D point class
   Vector  2D vector class, inherits from Point requires 2 points
   '''

class Point:
  '''enter x,y pair, a list/tuple, scalar or empty (null point)'''

#initialize, print, basic math
  def __init__(self, *args):
    '''initial values'''
    self.x = None;  self.y = None
    if len(args) == 2:   # two numbers, change to >= 2 for homog/3D pnts
      self.x = float(args[0])
      self.y = float(args[1])
    elif len(args) == 1: # list/tuple
      self.x = float(args[0][0])
      self.y = float(args[0][1])

  def __initold__(self, *args):
    '''initial values'''
    self.x = None;  self.y = None
    if len(args) == 2:   # two numbers, change to >= 2 for homog/3D pnts
      self.x = float(args[0])
      self.y = float(args[1])
    elif len(args) == 1: # list/tuple/scalar
      try:
        self.x = float(args[0][0])
        self.y = float(args[0][1])
      except:
        self.x = float(args[0])
        self.y = float(args[0])
        
  def __repr__(self):
    '''return a point as a string: called by the repr() and str().'''
    try:
      return '[%s,%s]' % (self.x, self.y)
    except:
      return '%s' % (self)

  def __add__(self, other):
    '''add a point, list or scalar'''
    other = to_point(other)
    return Point(self.x + other.x, self.y + other.y)
    
  def __div__(self, other):
    '''divide by a point, list or scalar'''
    other = to_point(other)
    return Point(self.x / other.x, self.y / other.y)

  def __mul__(self, other):
    '''multiply by a point, list or scalar'''
    other = to_point(other)
    return Point(self.x * other.x, self.y * other.y)
 
  def __sub__(self, other):
    '''subtract a point, list or scalar'''
    other = to_point(other)
    return Point(self.x - other.x, self.y - other.y)

  def __radd__(self, other):
    '''right add'''
    other = to_point(other)
    return self.__add__(other)

  def __rdiv__(self, other):
    '''right divide'''
    other = to_point(other)
    return other.__div__(self)

  def __rmul__(self, other):
    '''right multiply'''
    other = to_point(other)
    return self.__mul__(other)

  def __rsub__(self, other):
    '''right subtract'''
    other = to_point(other)
    return other.__sub__(self)

  def __iadd__(self, other):
    '''add in place'''
    other = to_point(other)
    return self.__add__(other)

  def __idiv__(self, other):
    '''divide in place'''
    other = to_point(other)
    return self.__div__(other)

  def __isub__(self, other):
    '''subtract in place'''
    other = to_point(other)
    return self.__sub__(other)

  def __imul__(self, other):
    '''multiply in place'''
    other = to_point(other)
    return self.__mul__(other)
  
#other math
  def log(self):
    '''Complex logarithm.  Undefined for Point(0,0)'''
    ln_r = math.log(math.hypot(self.x, self.y))
    theta = math.atan2(self.x, self.y)
    return Point(self.length(), math.radians(self.angle()))

  def sqr(self):
    '''square coordinates'''
    return Point(self.x * self.x, self.y * self.y)
 
  #Get/set/change point attributes
 
  def get_x(self):
    '''get the x coordinate'''
    return self.x

  def get_y(self):
    '''get the y coordinate'''
    return self.y 

  def set_x(self, x):
    '''set the x coordinate'''
    if isinstance(x, (int, float)):
      self.x = float(x)
      return self.x
    else:
      raise TypeError, "A numeric value is required for the x coordinate"

  def set_y(self, y):
    '''set the y coordinate'''
    if isinstance(y, (int, float)):
      self.y = float(y)
      return self.y
    else:
      raise TypeError, "A numeric value is required for the y coordinate"


#other properties
  def angle(self):
    '''angle in degrees from origin (0,0)'''
    return math.degrees( math.atan2(self.y, self.x) )

  def length(self):
    '''distance/radius from origin (0,0)'''
    return math.hypot(self.x, self.y)

  def distance(self, other):
    '''return the Euclidian distance between two points'''
    other = to_point(other)
    dx = self.x - other.x;  dy = self.y - other.y
    return math.hypot(dx,dy)
  
  #Geometric operations  

  def move(self, dx, dy):
    '''moves an existing point shifted by dx and dy
    see  translate if you want to create a new point'''
    self.set_x(self.x + dx); self.set_y(self.y + dy)
    return self
  
  def perpend(self):
    '''returns perpendicular point'''
    return Point(-self.y, self.x)
  
  def rotate(self, theta):
    '''returns a point rotated by theta degrees'''
    theta = math.radians(theta)
    c = math.cos(theta); s = math.sin(theta)
    x = self.x;  y = self.y
    x1 = x * c - y * s;  y1 = x * s + y * c
    return Point(x1, y1)

  def scale(self, a, b):
    '''returns a point scaled by a and b for the x and y direction'''
    return Point(self.x * a, self.y * b)
  
  def translate(self, dx, dy):
    '''returns a point shifted by dx and dy (see move as well)'''
    return Point(self.x + dx, self.y + dy)

#Conversion
def to_point(other):
  '''converts a list/tuple to a point'''
  if isinstance(other, Point):
    return other
  else:
    return Point(other)
  
def list_to_points(aList):
  '''convert a list of x,y pairs to point objects'''
  pnts = []
  for vals in aList:  #assumes vals = [x,y,...]
    try:
      pnts.append(Point(vals[0], vals[1]))
    except:
      print "Not a number: " + str(vals)
  return pnts

def points_to_list(pnts):
  '''convert point objects to a list of lists [[1,1],[2,2]]'''
  aList = []
  for pnt in pnts:
    aList.append([pnt.x, pnt.y])
  return aList

#Statistical
def center(pnts):
  '''average x, y coordinate for points'''
  n = len(pnts)
  p = sum_pnts(pnts)
  return Point(p.x / n, p.y / n)

def center_extent(pnts):
  '''center of point extent'''
  n = len(pnts)
  L, R, B, T = extent(pnts)
  Xcent = L + (R - L) / 2.0; Ycent = B + (T - B) / 2.0
  return Point(Xcent, Ycent)

def extent(pnts):
  '''extent of points, returns L, R, B, T'''
  n = len(pnts)
  L = 1.0e150; R = 1.0e-150
  B = 1.0e150; T = 1.0e-150
  for pnt in pnts:
    L = min([pnt.x, L]); R = max([pnt.x, R])
    B = min([pnt.y, B]); T = max([pnt.y, T])
  return [L, R, B, T]
  
def get_xs_ys(pnts):
  '''list of points, return x, y coordinates as separate lists'''
  Xs = [];  Ys = []
  if isinstance(pnts[0], (Point)):
    Xs = map((lambda pnt: pnt.x), pnts)  #Get the Xs
    Ys = map((lambda pnt: pnt.y), pnts)  #Get the Ys
  elif isinstance(pnts[0], (list, tuple)):
    Xs = map((lambda pnt: pnt[0]), pnts)
    Ys = map((lambda pnt: pnt[1]), pnts)
  return [Xs,Ys]

def momentsOld(pnts, cent_pnt):
  '''points, center pnt: returns, variances, std devs and
  covariance for points'''
  n = len(pnts)
  pnts_trans = map(lambda pnt: (pnt - cent_pnt), pnts)    #translate 
  xx_yy = sum(map(lambda pnt: pnt * pnt, pnts_trans))/n   #sum squares
  covar = sum(map(lambda pnt: pnt.x * pnt.y, pnts_trans))/n #covar
  var_x = xx_yy.x          #var x
  var_y = xx_yy.y          #var y
  s_x = math.sqrt(var_x)   #std x
  s_y = math.sqrt(var_y)   #std y
  return [var_x, var_y, s_x, s_y, covar]

def moments(pnts, cent_pnt):
  '''points, center pnt: returns, variances, std devs and
  covariance for points'''
  n = len(pnts)
  pnts_trans = map(lambda pnt: (pnt - cent_pnt), pnts)     #translate
  xx_yy = map(lambda pnt: pnt.sqr(), pnts_trans)
  xx_yy = sum_pnts(xx_yy) / [n,n]   #sum squares
  covar = sum(map(lambda pnt: pnt.x * pnt.y, pnts_trans))/n #covar
  var_x = xx_yy.x          #var x
  var_y = xx_yy.y          #var y
  s_x = math.sqrt(var_x)   #std x
  s_y = math.sqrt(var_y)   #std y
  return [var_x, var_y, s_x, s_y, covar]

def sum_pnts(pnts):
  '''sum the x,y coordinates of points'''
  n = len(pnts)
  xs = 0.0; ys = 0.0
  for pnt in pnts:
    xs += pnt.x
    ys += pnt.y
  return Point(xs, ys)


#Sorting
def sort_lex(pnts):
  '''sort points lexicographically in-place'''
  p = points_to_list(pnts)
  p.sort()  #list sort method
  p = list_to_points(p)
  return p

def sort_radial(pnts, cent):
  '''performs a radial sort about the center point'''
  sorted_pnts =[]
  out_pnts = []
  for pnt in pnts:
    p_angle = (pnt - cent).angle()
    sorted_pnts.append([p_angle, pnt])
  sorted_pnts.sort()
  sorted_pnts.reverse()
  for i in sorted_pnts:
    out_pnts.append(i[1])
  return [out_pnts, sorted_pnts]
    
def sort_dist(pnts, source):
  '''sorts points by distance from a source point''' 
  sorted_pnts =[]
  out_pnts = []
  for pnt in pnts:
    dist = source.distance(pnt)
    sorted_pnts.append([dist, pnt])
  sorted_pnts.sort()
  for i in sorted_pnts:
    out_pnts.append(i[1])
  return [out_pnts, sorted_pnts]

#Transformation
def standardize_pnts(pnts):
  '''standardize and rotate points'''
  '''
   (Section 6.2 in paper)
  
   In:  arbitrary collection of points.
   Out: An affine transformation has been applied to the points
        to place their means at (0,0), make their SDs equal to 1
        (except in degenerate--collinear--cases), and their
        correlation coefficient zero.
  ''' 
  n = len(pnts)
  #
  # Find the center and translate the points
  cent = center(pnts)
  x_c = cent.x; y_c = cent.y
  pnts_trans = map(lambda pnt: (pnt - cent), pnts)
  #
  # Calculate the standard deviations and trap small values
  xx_yy = map(lambda pnt: pnt.sqr(), pnts_trans)
  xx_yy = sum_pnts(xx_yy) / [n,n]   #sum squares
  s_x = math.sqrt(xx_yy.x)
  s_y = math.sqrt(xx_yy.y)

  if s_x == 0.0:
    x_stand = map(lambda pnt: pnt.x, pnts_trans)
  else:
    x_stand = map(lambda pnt: pnt.x/s_x, pnts_trans)
  if s_y == 0.0:
    y_stand = map(lambda pnt: pnt.y, pnts_trans)
  else:
    y_stand = map(lambda pnt: pnt.y/s_y, pnts_trans)
  #
  # Rotate the coordinates and compute the (squared)
  #   correlation coefficient
  rho = sum(map((lambda x,y: x*y), x_stand, y_stand))/n
  #  
  pnts_stand = []
  # Oct 8  collinear data can cause rho to be > +/- 1.0
  #        or not equal to one due to floating point errors
  One = 1.0 - 10**-14  
  if abs(rho) >= One:
    if rho < 0.0:
      rho = -1.0
    else:
      rho = 1.0
  if (rho > -1.0):
    denomX = 1.0 / math.sqrt(2.0*(1.0 + rho))
  else:
    denomX = 1.0
  if (rho < 1.0):
    denomY = 1.0 / math.sqrt(2.0*(1.0 - rho))
  else:
    denomY = 1.0
  u_sum = 0.0
  v_sum = 0.0
  #
  #compute the scaled coordinates
  for i in range(n):
    x = (x_stand[i] + y_stand[i]) * denomX
    y = (x_stand[i] - y_stand[i]) * denomY
    u_sum = u_sum + x
    v_sum = v_sum + y
    pnts_stand.append(Point(x,y))
  u = u_sum/n
  v = v_sum/n
  #
  return [pnts_stand, x_c, y_c, s_x, s_y, rho, u, v]

def transform_back(pnts, x_c, y_c, s_x, s_y, rho):
  '''points, x_c, y_c, s_x, s_y, corr coeff'''
  #  takes a series of standardized coordinates from
  #  and transforms them back.
  #  Get input values from standardize_pnts method
  #
  n = len(pnts)
  Xs, Ys = get_xs_ys(pnts)
  #
  #undo the scaling in the x and y
  if (rho > -1.0):
    scale_x = math.sqrt(2.0*(1.0 + rho))
  else:
    scale_x = 1.0
  if (rho < 1.0):
    scale_y = math.sqrt(2.0*(1.0 - rho))
  else:
    scale_y = 1.0
  #
  pnts = []
  X1 = map(lambda x: x * scale_x, Xs)   #scale x
  Y1 = map(lambda y: y * scale_y, Ys)   #scale Y
  Xs = map(lambda x,y: ((x+y)/2.0)*s_x + x_c, X1,Y1)  #rotate/translate x
  Ys = map(lambda x,y: ((x-y)/2.0)*s_y + y_c, X1,Y1)  #rotate/translate y
  #pnts =  map((lambda x,y: [x,y]), Xs, Ys)  #old in list form
  pnts =  map((lambda x,y: Point(x,y)), Xs, Ys)
  return pnts


class Vector(Point):
  '''enter 2 points or dx, dy'''
 
  def __init__(self, p1, p2):
    '''initialization from points or dx, dy'''
    if isinstance(p1, Point) and isinstance(p2, Point):
      self.x = p2.x - p1.x
      self.y = p2.y - p1.y
      self.start = p1
      self.end = p2
    else:
      self.x = float(p1)
      self.y = float(p2)
      self.start = Point(0,0)
      self.end = Point(p1,p2)

  def angle(self, other = None):
    '''angle between 2 vectors or the x-axis, range -pi to pi'''
    self_angle = math.atan2(self.y, self.x)
    if other == None:
      return math.degrees(self_angle)
    else:
      other_angle = math.atan2(other.y, other.x)
      a = abs(self_angle - other_angle)
      if a > math.pi:
        a = a - math.pi
      return math.degrees(a)

  def dot(self, other):
    '''dot product between 2 vectors'''
    return self.x * other.x + self.y * other.y

  def length(self):
    '''vector length'''
    return math.hypot(self.x, self.y)

  def project(self, other):
    '''project vector self onto vector other and return a point'''
    vec_len = other.length()
    if vec_len > 0.0:
      val = (self.dot(other)) / vec_len
      return other.unit() * [val, val]
    else:
      print "Vector length is zero, returning the original vector"
      return self
    
  def unit(self):
    vec_len = self.length()
    if vec_len > 0.0:
      x = self.x / vec_len
      y = self.y / vec_len
      return Vector(x, y)
    else:
      print "Vector length is zero, returning the original vector"
      return self

#-------------------------------------------------------------------- 
if __name__ == "__main__":
  print "Py_Points loaded"
  ell = [[3,3],[6,9],[12,10],[15,5],[13,2.5]]  #favorite ellipse
  #ell = [[0,0],[0,2],[3,1]]  #Figure 3.15? in report
  pnts = list_to_points(ell)
  print "input points", pnts
  print "moments ",moments(pnts, center(pnts))
  pnts_stand, x_c, y_c, s_x, s_y, rho, u, v = standardize_pnts(pnts)
  print "standardized points", pnts_stand
  back_pnts = transform_back(pnts_stand, x_c, y_c, s_x, s_y, rho)
  print "tranformed back", back_pnts
