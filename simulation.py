import time
from matplotlib import pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import numpy as np
from shapely import intersection
import multiprocessing

def triangle(side):
    center = (np.random.rand()*side, np.random.rand()*side)
    Triangle_side = 2*np.sqrt(np.pi/np.sqrt(3))
    Triangle_hight = np.sqrt(3)/2*Triangle_side
    points = [
        (center[0],center[1]+2/3*Triangle_hight),
        (center[0]-Triangle_side/2,center[1]-1/3*Triangle_hight),
        (center[0]+Triangle_side/2,center[1]-1/3*Triangle_hight)
    ]
    return points

def next(polys, anim,side):
    poly = Polygon(triangle(side))
    #poly = Point((np.random.rand()*side, np.random.rand()*side)).buffer(1)

    polys.append(poly)
    mergedPolys = unary_union(polys)

    polys = []
    if mergedPolys.geom_type == "Polygon":
        polys.append(mergedPolys)

    elif mergedPolys.geom_type == "MultiPolygon":
        for poly in mergedPolys.geoms:
            polys.append(poly)

    return polys
    

def left_right(anim,side):
    iter = 0
    polys = []
    while True:
        iter += 1
        polys = next(polys, anim,side)

        # Check if any group touches both the left and right wall
        for poly in polys:
            if poly.bounds[0] <= 0 and poly.bounds[2]>= side:
                return iter, polys


def run_trial(n,animate,side):

    left_right_n, polys = left_right(animate,side)

    print(f"triangles required to connect left and tight sides for n = {n} is {left_right_n}")

    i = left_right_n


    box = Polygon([(0,0), (0,side), (side,side), (side,0)])

    while True:
        i += 1
        polys = next(polys, animate,side)
        if(i%100==0):
            print(i,)
        if intersection(unary_union(polys), box).area == box.area:
            break
    
    print(f"triangles required to fill square for n = {n} is {i}")

    return left_right_n, i




# trials = np.array([run_trial(n, animate) for _ in range(num_trial)])
# print(np.mean(trials[:, 0]))
# print(np.mean(trials[:, 1]))

#run_trial(n, animate)



"""
Tests
___________________________
n = 100, runs = 100
25.91
399.67
___________________________



"""
if __name__ == "__main__":

    n = 1000 # area
    side = np.sqrt(n)
    num_trial = 1
    animate = False

    manager = multiprocessing.Manager()
    fillSquareList = manager.list()

    workers = [multiprocessing.Process(target=run_trial, args=(n,animate,side), daemon=True) for i in range(num_trial)]

    print("Starting")
    for w in workers:
        w.start()
    print("Waiting")
    for w in workers:
        w.join()
    print("Done")
    for i in fillSquareList:
        print(i)