import time
from matplotlib import pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
from shapely import intersection

Triangle_side = 2*np.sqrt(np.pi/np.sqrt(3))
Triangle_hight = np.sqrt(3)/2*Triangle_side

n = 100 # area
side = np.sqrt(n)
num_trial = 1000

animate = True
# animate = False

def axes_config():
    ax.clear()
    ax.axis('equal')
    ax.plot((0,0),(0,side), c="black")
    ax.plot((side,side),(0,side), c="black")
    ax.set_xlim((0, side))
    ax.set_ylim((0, side))

def triangle(center = (np.random.rand()*side, np.random.rand()*side)):
    points = [
        (center[0],center[1]+2/3*Triangle_hight),
        (center[0]-Triangle_side/2,center[1]-1/3*Triangle_hight),
        (center[0]+Triangle_side/2,center[1]-1/3*Triangle_hight)
    ]
    return points
    

def next(polys, anim = False):
    poly = Polygon(triangle((np.random.rand()*side, np.random.rand()*side)))
    polys.append(poly)
    mergedPolys = unary_union(polys)

    polys = []
    if mergedPolys.geom_type == "Polygon":
        polys.append(mergedPolys)

    elif mergedPolys.geom_type == "MultiPolygon":
        for poly in mergedPolys.geoms:
            polys.append(poly)

    if anim:
        axes_config()
        gpd.GeoSeries([mergedPolys]).boundary.plot(ax=ax)
        plt.draw()
        plt.pause(0.001)
        time.sleep(0.01)
    return polys
    

def left_right(anim = False):
    iter = 0
    polys = []
    while True:
        iter += 1
        polys = next(polys, anim)

        # Check if any group touches both the left and right wall
        for poly in polys:
            if poly.bounds[0] <= 0 and poly.bounds[2]>= side:
                return iter, polys


def run_trial(n = 100, animate = False):

    left_right_n, polys = left_right(animate)

    print(f"triangles required to connect left and tight sides for n = {n} is {left_right_n}")

    i = left_right_n


    box = Polygon([(0,0), (0,side), (side,side), (side,0)])

    while True:
        i += 1
        polys = next(polys, animate)
        if intersection(unary_union(polys), box).area == 100.0:
            break
    
    print(f"triangles required to fill square for n = {n} is {i}")

    return left_right_n, i


if animate:
    fig, ax = plt.subplots()
    axes_config()

# trials = np.array([run_trial(n, animate) for _ in range(num_trial)])
# print(np.mean(trials[:, 0]))
# print(np.mean(trials[:, 1]))

run_trial(n, animate)

if animate:
    plt.show()



"""
Tests
___________________________
n = 100, runs = 100
25.91
399.67
___________________________



"""