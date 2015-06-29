'''
Py_Points_Demo.py

Author
  D.E. Patterson

Created  Aug, 2008
Updates  June 2013

Requires:  random, Py_Points

'''
from Py_Points import * #use this option to use methods directly
import random

print "\n","Point class function demo"
print "\n", "1.  create points:"
print "      from coordinates: Point(1,1) ", Point(1,1)
print "      from list:  Point([10,10])   ", Point([10,10])
print "      a null point: Point()        ", Point() 
print "2.  math with points"
print "    sums/differences/translation: "
print "      Point(1,1) + list [5,5]:",  Point(1,1) + [5,5]
print "      list [3,2] + Point(1,1):", [3,2] + Point(1,1)
p1 = Point(1,1); p2 = Point(5,5)
print "       p1 = Point(1,1), p2 = Point(5,5): "
print "       x-diff, p1.x - p2.x: ", p1.x - p2.x
print "       y diff, p1.y - p2.y: ", p1.y - p2.y
print "       p1 - (5,5):          ", p1 - [5,5]
print "    multiplication/division/scaling:"
print "      Point(3,2) * list [5,5]: ",  Point(3,2) * [5,5]
print "      Point(3,2) / list [2,2]: ",  Point(3,2) / [2,2]
#
#list to points and points to list example
aList = [[1,2],[2,2],[3,3]]
pnts = list_to_points(aList)
print "3.  List to points: ", pnts
aList = points_to_list(pnts)
print "4.  Points to List: ", aList
print "5.  point distance"
print "    Point(1,1) to Point(2,2)", Point(1,1).distance(Point(2,2))
print "6.  set/get example:"
print "     Point(1,1), set_x to 5: ", pnts[0].set_x(5)
print "     Point(3,2), get_x     : ", Point(3,2).get_x()
print "7.  move Points: "
print "      Point(1,1).move(5,5):    ", Point(1,1).move(5,5)
print "      Point(1,1) + Point(5,5): ", Point(1,1) + Point(5,5)
print "      Point(1,1) - [3,2]:    : ", Point(1,1) - [3,2]
print "8.  angles:"
print "      Point(1,1).angle():  ", Point(1,1).angle()
print "      Point(-1,1).angle(): ", Point(-1,1).angle()
print "9.  rotation:"
print "      Point(1,1).rotate(45):   ", Point(1,1).rotate(45)
print "      Point(1,1).rotate(-135): ", Point(1,1).rotate(-135)
#
ell = [[3,3],[6,9],[12,10],[15,5],[13,2.5]]  #favorite ellipse
pnts = list_to_points(ell)
print "10. standardized points: "
theReturned = standardize_pnts(pnts)
standPnts, Xavg, Yavg, Xstd, Ystd, rho, u, v = theReturned
print "\t","input and standardized"
for i in range(len(pnts)):
  print "\t", pnts[i], ", ", standPnts[i]

headers = ["Xavg", "Yavg", "Xstd", "Ystd", "rho", "u", "v"]
for i in range(0,len(headers)):
  print "\t", headers[i],theReturned[i+1]

print "11. points translated back: "
originalPnts = transform_back(standPnts, Xavg, Yavg, Xstd, Ystd, rho)
for i in originalPnts:
  print "\t", str(i)
#
#Vector class examples
p0 = Point(0,0)  #origin point
p1 = Point(1,1)
p2 = Point(2,3)
p3 = Point(4,5)
print "\n", "Vector Class examples"
print "1.  points p0, p1, p2, p3", p0, p1, p2, p3
v1 = Vector(p0,p1)
v2 = Vector(p1,p2)
v3 = Vector(p2, p3)
print "2.  vector create test"
print "    v1 = p0, p1 (", p0, p1, "): ", v1
print "    v2 = p1, p2 (", p1, p2, "): ", v2
print "    v3 = p2, p3 (", p2, p3, "): ", v3
print "3.  perpendicular of v1 (", v1, "): ", v1.perpend()
print "4.  v1", v1, "rotated by 15 degrees", v1.rotate(15)
print "5.  length of v1", v1,": ", v1.length() 
dotProd = v1.dot(v2)
print "6.  Dot product v1,", v1, "and point", Point(2,2), "=", dotProd
print "7.  unit test of v1:", v1.unit()
print "8.  vector math  v1/v2:", v1, v2, "=", v1/v2
print "9. projection of v1 onto v3 ", v1.project(v3)
print "10. angle (0,0) to (1,0):  ", Vector(1,0).angle()
print "    angle (0,0) to (1,1):  ", Vector(1,1).angle()
print "    angle (0,0) to (-1,1): ", Vector(-1,1).angle()
print "    angle (1,1) to (-1,1): ", Vector(1,1).angle(Vector(-1,1))
print "\n", "Statistical and other examples"
print 
pnts = []
for i in range(5):
  pnts.append(Point(random.random(), random.random()))
print "1.  input points:  ", pnts
cent = center(pnts)
var_x, var_y, std_x, std_y, covar  = moments(pnts, cent)
print "2.  center point p0..p4", cent
print "    variance x, y for p0..p4", var_x, var_y
print "    std dev  x, y for p0..p4", std_x, std_y
print "    covariance       ", covar
print "3.  sort options"
lexSort = sort_lex(pnts)
print "    lexicographical sort: "
for i in lexSort:
  print "\t", i
newPnts, withAngle = sort_radial(pnts, cent)
print "    radial sort: "
for i in newPnts:
  print "\t", i
print "    with angle"
for i in withAngle:
  print "\t", i
newPnts, withDist = sort_dist(pnts, cent)
print "    dist. to center sort: "
for i in newPnts:
  print "\t", i
print "     with distance"
for i in withDist:
  print "\t", i
