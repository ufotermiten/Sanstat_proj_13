import time
from matplotlib import pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import numpy as np
from shapely import intersection
import multiprocessing
import csv

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

def next(polys,side,iter,shape):
    if shape =='Circle':
        poly = Point((np.random.rand()*side, np.random.rand()*side)).buffer(1)
    elif shape == 'Triangle':
        poly = Polygon(triangle(side))
    polys.append(poly)
    mergedPolys = unary_union(polys)
    if(iter%10 == 0):
        box = Polygon([(0,0), (0,side), (side,side), (side,0)])
        mergedPolys = intersection(mergedPolys,box)
    polys = []
    if mergedPolys.geom_type == "Polygon":
        polys.append(mergedPolys)

    elif mergedPolys.geom_type == "MultiPolygon":
        for poly in mergedPolys.geoms:
            polys.append(poly)
    return polys
    
def left_right(side,shape):
    iter = 0
    polys = []
    while True:
        iter += 1
        polys = next(polys,side,iter,shape)

        # Check if any group touches both the left and right wall
        for poly in polys:
            if poly.bounds[0] <= 0 and poly.bounds[2]>= side:
                return iter, polys

def run_trial(left_right_list,fill_list,side,shape):

    left_right_n, polys = left_right(side,shape)

    #print(f"triangles required to connect left and tight sides for n = {n} is {left_right_n}")

    i = left_right_n


    box = Polygon([(0,0), (0,side), (side,side), (side,0)])

    while True:
        i += 1
        polys = next(polys,side,i,shape)
        if intersection(unary_union(polys), box).area == box.area:
            break
    
    #print(f"triangles required to fill square for n = {n} is {i}")
    left_right_list.append(left_right_n)
    fill_list.append(i)
    return left_right_n, i



"""
Tests
___________________________
n = 100, runs = 100
25.91
399.67
___________________________
___________________________
Triangle n=10000, runs = 8
Mean of left right:  2348.25
[2338, 2268, 2250, 2479, 2254, 2518, 2366, 2313]
Mean of fill:  57356.375
[53452, 45398, 57416, 61918, 69633, 56701, 58015, 56318]
___________________________

"""
if __name__ == "__main__":
    # shape = 'Circle'
    shape = 'Triangle'
    n = 100 # area
    side = np.sqrt(n)
    num_trial = 1001
    
    manager = multiprocessing.Manager()
    left_right_list = manager.list()
    fill_list = manager.list()
    for j in range(int(num_trial/(multiprocessing.cpu_count()-1))):
        workers = [multiprocessing.Process(target=run_trial, args=(left_right_list,fill_list,side,shape), daemon=True) for i in range(multiprocessing.cpu_count()-1)]
        print("Starting")
        for w in workers:
            w.start()
        print("Waiting")
        for i,w in enumerate(workers):
            w.join()
    print('Mean of left right: ', np.mean(left_right_list)) 
    print('Mean of fill: ', np.mean(fill_list))
    
    valuefile = open("Sanstat_proj_13/values.txt",'a')
    valuefile.write(
f"""__________
Shape: {shape}
Area: {n}
Number of Trials: {num_trial}
Mean of left-right: {np.mean(left_right_list)}
Mean of fill: {np.mean(fill_list)}
__________
""")
    datafile = open('Sanstat_proj_13/data.csv','a')
    write = csv.writer(datafile)
    write.writerow(['fill',shape,n,num_trial,fill_list])
    write.writerow(['lr',shape,n,num_trial,left_right_list])
    print("Done")