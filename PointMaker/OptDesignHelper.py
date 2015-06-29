#OptDesignHelper.py
#
#OptDesign comments
  #OptDesign(v, nDim As Integer, n As Long, MaxIterNum As Integer, 
  #  Threshold As Double)
  # 
  #  Return the optimal weights lambda(n).  Points with lambda close to zero
  #  are inside the MABE; the other points lie on ("support") the MABE.
  #  The maximum individual variance, normalized, will be within 'Threshold'
  #  of 1.0.
  # 
  #  After DM Titterington, 1978.
  #  WAH @ QD, 30 June 2008.
  #  7 July 2008: Harman and Pronzato, "Improvements on removing non-optimal
  #               support points in D-optimum design algorithms," 2007.
  # 
  #  NB: Repeated points are OK.
  #  Collinear points will cause M to be singular; computing a pseudo-inverse
  #  (with SVD) would probably solve this problem.
  # 
  #  nDim enables this to handle higher dimensions!
  # 
  #  v(n, 2) contains (x, y).
  #  u(n, nDim + 1) [v; 1]
  #  ndx(n)                Active points in u[]
  #  mq                    Number of active points
  #  IterNum               Current IterNumation
  #  lambda(n)             Non-negative weights for the points
  #  i, iq                 Always a point index
  #  j, k                  Always variable indexes in 1..nDim+1
  #  x, y
  #  M(nDim + 1, nDim + 1) Information and var-cov matrix
  #  needsNormalization    Boolean
  #  d(n)                  Implements Pronzato's optimization
  #  e, h                  Values in Pronzato's inequality
  #  maxX, xSum, xSumPlus
#-------------------------------------------------------------
#Main
#
#Imports
import os, sys, string, math, time
from Py_Points import *
import py_gp_methods

#-------------------------------------------------------------  
def matrixMake(r,c,aVal):
  #
  # Create an empty matrix with values
  # r     number of rows
  # c     number of columns
  # aVal  a value or a list
  #
  A = []
  for i in range(r):
    row = []
    for j in range(c):
      row.append(aVal)
    A.append(row)
  return A


def getXsYs(pnts):
  #
  # Get the x and y coordinates of an array of points as separate lists.
  # (Facilitates standardization and related calculations.)
  #
  Xs = map((lambda pnt: pnt[0]), pnts)  #Get the Xs
  Ys = map((lambda pnt: pnt[1]), pnts)  #Get the Ys
  return [Xs,Ys]


def supportPnts(pnts, indices):
  suppPnts = []
  for i in indices:
    suppPnts.append(pnts[i])  
  return suppPnts


def standardizePnts(pnts):
  #
  # Standardizes and rotates points.
  # (Section 6.2 in paper)
  #
  # In:  arbitrary collection of points.
  # Out: An affine transformation has been applied to the points
  #      to place their means at (0,0), make their SDs equal to 1
  #      (except in degenerate--collinear--cases), and their
  #      correlation coefficient zero.
  #
  #--> (WAH added code to trap exceptions.)
  #
  n = len(pnts)
  Xs, Ys = getXsYs(pnts)
  # Find the center (means).
  Xavg = sum(Xs)/n
  Yavg = sum(Ys)/n
  # Recenter the points.
  dx = map(lambda x: (x - Xavg), Xs)   # x - mean list
  dy = map(lambda y: (y - Yavg), Ys)   # y - mean list
  #
  # Compute the SDs.
  Xstd = math.sqrt(sum(map(lambda x: x*x, dx))/n)  #X std dev
  Ystd = math.sqrt(sum(map(lambda y: y*y, dy))/n)  #Y std dev
  #
  # Standardize the points.
  #--> We trap very small values of Xstd or Ystd.
  #
  if Xstd == 0.0:
    Xstand = dx
  else:
    Xstand = map(lambda x: x/Xstd, dx)
  
  if Ystd == 0.0:
    Ystand = dy
  else:
    Ystand = map(lambda y: y/Ystd, dy)
  #
  # Compute the (squared) correlation coefficient.
  #
  rho = sum(map((lambda x,y: x*y), Xstand, Ystand))/n
  #
  # Rotate the standardized values.
  #
  pntsStand = []
  if (rho > -1.0):
    denomX = 1.0 / math.sqrt(2.0*(1.0 + rho))
  else:
    denomX = 1.0

  if (rho < 1.0):
    denomY = 1.0 / math.sqrt(2.0*(1.0 - rho))
  else:
    demonY = 1.0

  uSum = 0.0
  vSum = 0.0
  for i in range(n):
    x = (Xstand[i] + Ystand[i]) * denomX
    y = (Xstand[i] - Ystand[i]) * denomY
    uSum = uSum + x
    vSum = vSum + y
    pntsStand.append([x,y])
  u = uSum/n
  v = vSum/n
  #print "Xavg, Yavg, Xstd, Ystd", Xavg, Yavg, Xstd, Ystd, u, v
  #print "correl coeff", rho
  #print "stand pnts", pntsStand
  return [pntsStand, Xavg, Yavg, Xstd, Ystd, rho, u, v]

  
def OptDesign(v, nDim, MaxIter, Threshold):
  #
  # v          an array of points (x,y)
  # nDim       number of dimensions
  # n          number of points
  # MaxIter    maximum number of iterations 
  # Threshold  termination threshold
  #
  Zero = 10**-12           # Practically zero #--> See page 15
  Rho = 2.0                # Normalization factor >= 1
  n = len(v)
  #
  #   Create u = [v; 1] and indexes for the active points,
  #   ndx[].  Initialize the solution, lambda[].
  #
  u = matrixMake(n, nDim + 1, 0.0)
  d = matrixMake(n,1,0.0)
  x = 1.0/n; ndx = [];  Lambda = []
  for i in range(n):
    for j in range(nDim):
      u[i][j] = v[i][j]
    u[i][nDim] = 1.0
    ndx.append(i)
    Lambda.append(x)
  #
  mq = n      # Number of active points
  # 
  #   Iteratively improve the solution.
  #
  IterNum = 0
  Start = time.clock()  # start time
  TimeMQ = [[IterNum, mq, 0.0]]
  #
  while IterNum <= MaxIter:
    #
    #   Compute the information matrix M.
    #
    M = matrixMake(nDim+1, nDim+1, 0.0)
    
    for iq in range(mq):
      i = ndx[iq]
      for j in range(nDim+1):
        for k in range(nDim+1):
          M[j][k] = M[j][k] + Lambda[i]*u[i][j]*u[i][k]
    # 
    #   Invert it in place to obtain the asymptotic
    #   variance-covariance matrix.  The last coefficient
    #   normalizes the inverse.
    #
    M = inverseMatrix(M, nDim+1.0) #--> Note the normalization!
    #
    #   Update the weights, lambda, which are normalized
    #   variances.
    # 
    maxX = 1.0                    # Compute Pronzato's optimization
    for iq in range(mq):
      i = ndx[iq]
      x = 0.0                     # The (normalized) variance at # i
      for j in range(nDim+1):
        for k in range(nDim+1):
          x = x + u[i][j] * M[j][k] * u[i][k]
      Lambda[i] = Lambda[i] * x
      # 
      #   Pronzato: track the largest value of the variance
      #   and save it for thinning the active set.
      # 
      if x > maxX:
        maxX = x
      d[i] = x
    e = (nDim + 1) * (maxX - 1.0)    # Always non-negative
    if e <= Threshold:
      # We satisfied the minimax criterion
      break
      # 
      #   Remove active points according to Pronzato's criterion.
      # 
    h = (2.0 + e - math.sqrt(e * (4.0 + e - 4.0 / (nDim + 1)))) / 2.0
    h = h - 0.00000000000001  #h - 1.0 E-14
    #
    needsNormalization = False
    xSum = 0.0; xSumPlus = 0.0
    #
    for iq in range(mq-1,-1,-1): #= mq To 1 Step -1
      i = ndx[iq]
      if d[i] < h:          # Remove the point.
        Lambda[i] = 0.0     # Permanently zero the weight
        ndx[iq] = ndx[mq-1] # Swap this point out (#--> Note the index!)
        mq = mq - 1         # Shrink the array
        needsNormalization = True
      else:                 #   Accumulate the weight.
        if d[i] > 1.0:
          xSumPlus = xSumPlus + Lambda[i]
        else:
          xSum = xSum + Lambda[i]
    if needsNormalization:
      # 
      #   Suggestion of Harman and Pronzato: increase only
      #   the weights for the points with variance exceeding
      #   the minimax value of nDim+1.
      #
      xSum = xSum + Rho * xSumPlus
      for iq in range(mq):
        i = ndx[iq]
        if d[i] > 1.0: 
          Lambda[i] = Lambda[i] * Rho / xSum
        else:
          Lambda[i] = Lambda[i] / xSum
      needsNormalization = False
    else:
      # 
      #   Just force the weights to sum to unity
      #   without changing their relative sizes.
      # 
      xSum = xSum + xSumPlus
      for iq in range(mq): #= 1 To mq
        i = ndx[iq]
        Lambda[i] = Lambda[i] / xSum
    #
    #   Prepare to iterate.  Mark time
    #
    IterNum = IterNum + 1
    diffTime = time.clock() - Start
    TimeMQ.append([IterNum, mq, diffTime]) #,"Normalizing"])
    #
    #   (We could check whether the number of iterations has been
    #   exceeded, but don't bother.)
    # 
  #
  if IterNum < MaxIter:
    NIter = IterNum
  OptDesign = Lambda
  
  return ndx, mq, M, OptDesign, IterNum, TimeMQ #--> Note additional return values
  # 
  #   At this point, M contains an approximation to the MABE:
  #   it is the level set u'Mu = 1.  The MABE is supported by
  #   points in the set indexed by ndx[], most likely by those
  #   having the highest values of the weights lambda[].  These
  #   will also be the points for which the normalized variances
  #   stored in d[] are closest to 1.
  # 

def inverseMatrix(A, z):
  #
  # Inverts a 3x3 matrix
  #--> AND DIVIDES IT BY z.
  #
  n = len(A)
  assert n == 3, "3x3 matrix required"
  #
  aList = []
  for i in A:
    for j in i:
      aList.append(j)
  #
  a,b,c,d,e,f,g,h,i = aList
  #
  detA = a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
  if detA == 0.0:  #terminate if zero
    return None
  #
  outA = [[e*i - f*h, c*h - b*i, b*f - c*e],
         [f*g - d*i, a*i - c*g, c*d - a*f],
         [d*h - e*g, b*g - a*h, a*e - b*d]]
  invdet = 1.0/(z * detA) #-->This takes care of the division
  for i in range(n):
    for j in range(n):
      outA[i][j] = outA[i][j]*invdet
  #
  return outA 
 
