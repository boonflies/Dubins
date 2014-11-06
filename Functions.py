import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np




# returns the coordinates to draw a cylinder

def Cylinder(xCenter, yCenter, zCenter, r,n):
    '''
    Returns the unit cylinder that corresponds to the curve r.
    INPUTS:  r - a vector of radii
             n - number of coordinates to return for each element in r

    OUTPUTS: x,y,z - coordinates of points
    '''

    # ensure that r is a column vector
    r = np.atleast_2d(r)
    r_rows,r_cols = r.shape

    if r_cols > r_rows:
        r = r.T

    # find points along x and y axes
    points  = np.linspace(0,2*np.pi,n+1)
    x = np.cos(points)*r
    y = np.sin(points)*r

    # find points along z axis
    rpoints = np.atleast_2d(np.linspace(0,50,len(r)))
    z = np.ones((1,n+1))*rpoints.T

    x = x + xCenter
    y = y + yCenter
    z = z + zCenter

    return (x,y,z)


# returns the coordinates to draw a sphere
def Sphere(xCenter, yCenter, zCenter, r):
    #draw sphere
    u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:50j]
    x=np.cos(u)*np.sin(v)
    y=np.sin(u)*np.sin(v)
    z=np.cos(v)
    # shift and scale sphere
    x = r*x + xCenter
    y = r*y + yCenter
    z = r*z + zCenter
    return (x,y,z)

def Spheres(xcenter, ycenter, zcenter, r):
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)

    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    return x, y, z



