import numpy as np
import matplotlib.pyplot as plt
import time
import math


"""
Plan:

Create circles at random positions keeping track of all center points in a list.

Group the circles together if thay are touching.

Check if any group is touching both walls. If so the first problem is complete.

Continue adding circles until there is only one group. This means all circles are touching.

Check the border of each circle to find the position of holes in the mass of circles.

Continue generating circles, checking if they are close to any holes.

When all holes are gone we are done. Note the number of circles required.
"""
def zero_tup(r):
    return True if len(r) == 0 else (True if r[0][0] == 0 and r[0][1] == 0 else False)

def touching(p0,p1):
    return True if np.linalg.norm(p0 - p1) <=2 else False


# is_between checks if the angle mid is between start and end taking looping into account
def is_between(start, end, mid):
    end = end - start + np.pi*2 if (end - start) < 0.0 else end - start
    mid = mid - start + np.pi*2 if (mid - start) < 0.0 else mid - start
    return mid <= end

# inside checks if the angle range a1 is inside of a0
def inside(a0,a1):
    return True if is_between(*a0, a1[0]) and is_between(*a0, a1[1])  else False

# circle_overlap takes two points ane return the angles of their intersection points from the pov of the first point
# may cause error if called using non overlapping circles
def circle_overlap(p0, p1):
    d=np.linalg.norm(p0 - p1)
    
    a=(d**2)/(2*d)
    h=math.sqrt(1-a**2)
    x2=p0[0]+a*(p1[0]-p0[0])/d   
    y2=p0[1]+a*(p1[1]-p0[1])/d   
    x3=x2+h*(p1[1]-p0[1])/d     
    y3=y2-h*(p1[0]-p0[0])/d 

    x4=x2-h*(p1[1]-p0[1])/d
    y4=y2+h*(p1[0]-p0[0])/d
    
    return math.atan2(y3-p0[1],x3-p0[0])%(2*np.pi), math.atan2(y4-p0[1],x4-p0[0])%(2*np.pi)
   
# wall_overlap returns the angle ranges where a circle intersects with a wall 
def wall_overlap(p, side):
    rs = []
    if p[0] < 1:
        rs.append((np.pi-math.acos(p[0]), np.pi+math.acos(p[0])))
    elif p[0] > side-1:
        rs.append((-math.acos(side-p[0]), math.acos(side-p[0])))
    if p[1] < 1:
        rs.append((np.pi+math.asin(p[1]), -math.asin(p[1])))
    elif p[1] > side-1:
        rs.append((math.asin(side-p[1]), np.pi-math.asin(side-p[1])))

    return [np.array([x[0]%(2*np.pi), x[1]%(2*np.pi)]) for x in rs]


# combine_ranges combines all overlapping ranges. Returns [(0,0)] if the ranges span 2PI
def combine_ranges(rs):
    rs.sort(key=lambda x: x[0])
    if zero_tup(rs):
        return [(0,0)]
    i = 0
    while i < len(rs):
        old = rs[i]
        j = i+1
        while j < len(rs):
            # If the end points of two ranges are within the other range the entire circle is covered
            if inside(rs[i], rs[j]) and inside(rs[j], rs[i]):
                rs = [(0,0)]
                i = 0
                break

            # Remove angle ranges that are completely covered by another
            if inside(rs[i], rs[j]):
                rs.pop(j)
                continue
            if inside(rs[j], rs[i]):
                rs.pop(i)
                continue

            # Combine angle ranges that overlap
            if is_between(*rs[i], rs[j][0]):
                rs[i] = (rs[i][0],rs[j][1])
                rs.pop(j)
            elif is_between(*rs[i], rs[j][1]):
                rs[i] = (rs[j][0],rs[i][1])
                rs.pop(j)
            else:
                j += 1
        if list(rs[i]) == list(old):
            i += 1
    return rs

# new_overlap checks and updates the overlap only for the last point and the points it touches
def new_overlap(points, points_rs, new_point):
    rs = wall_overlap(new_point, side)
    for j, p1 in enumerate(points):
        d = np.linalg.norm(new_point - p1)
        if d <= 2 and d != 0:
            rs.append(circle_overlap(new_point,p1))
            points_rs[j].append(circle_overlap(p1,new_point))
            points_rs[j] = combine_ranges(points_rs[j])
    rs = combine_ranges(rs)
    # if zero_tup(rs):
    #     return points_rs
    points_rs.append(rs)
    return points_rs


# overlap checks the overlap of all points
def overlap(points):
    points_rs = []
    for i, p in enumerate(points):

        points_rs.append(wall_overlap(p, side))
        for j, p1 in enumerate(points):
            if j!=i: 
                d = np.linalg.norm(p - p1)
                if d <= 2 and d != 0:
                    points_rs[i].append(circle_overlap(p,p1))
        points_rs[i] = combine_ranges(points_rs[i])
    return points_rs


def gen_circle(anim = False):
    x = np.random.rand()*side
    y = np.random.rand()*side

    if anim:
        ax.add_patch(plt.Circle((x,y), 1))
        # ax.add_patch(plt.Circle((x,y), 1, fill=False))
        plt.draw()
        plt.pause(0.001)
        time.sleep(0.01)
    return x, y

def next(groups, anim = False):
    point = np.array(gen_circle(anim))
    groups.append([point])
    overlap = []
    for i, g in enumerate(groups[:-1]):
        for p in g:
            if touching(p, point):
                groups[i].append(point)
                overlap.append(i)
                break

    # remove last point if placed in other group
    if len(overlap) >= 1:
        groups.pop()

    # create new group from overlapping groups
    if len(overlap) > 1:
        new_group = []
        for i in overlap[::-1]:
            new_group = new_group + groups.pop(i)
        new_group.pop()
        groups.append(new_group)
    return groups
    

def left_right(iter, anim = False):
    groups = []
    for iterations in range(iter):
        groups = next(groups, anim)

        # Check if any group touches both the left and right wall
        for g in groups:
            left = False
            right = False
            for p in g:
                if p[0] <=1:
                    left = True
                if p[0] >= side-1:
                    right = True
            if left and right:
                return iterations+1, groups
    return iter, groups






def run_trial(n = 100, max_circles = 10000, animate = False):

    left_right_n, groups = left_right(max_circles, animate)

    if left_right_n == max_circles:
        print("reached max circles")
    else:
        print(f"circles required to connect left and tight sides for n = {n} is {left_right_n}")

    i = left_right_n

    points = []
    for g in groups:
        points += g
    # print(len(points))
    # print(groups)
    # print(points)

    # raise NotImplementedError

    while len(groups) != 1:
        i += 1
        # print(i)
        groups = next(groups, animate)


    points = []
    for g in groups:
        points += g

    # print("calc overlap")
    o = overlap(points)
    # print("overlap calc done")
    while True:
        i += 1
        # print(i)

        point = np.array(gen_circle(animate))
        l = len(o)
        o = new_overlap(points, o, point)
        if l != len(o):
            points.append(point)

        uncovered = []
        for x in o:
            if not zero_tup(x):
                uncovered.append(x)
        u = len(uncovered)
        # print(u)
        if u == 0:
            break

    print(f"circles required to fill square for n = {n} is {i}")
    

    return left_right_n, i


n = 100 # area
side = np.sqrt(n)
max_circles = 10000
num_trial = 100

animate = True
# animate = False


if animate:
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.plot((0,0),(0,side), c="black")
    ax.plot((side,side),(0,side), c="black")
    ax.set_xlim((0, side))
    ax.set_ylim((0, side))

# trials = np.array([run_trial(n, max_circles, animate) for _ in range(num_trial)])
# print(np.mean(trials[:, 0]))
# print(np.mean(trials[:, 1]))

run_trial(n, max_circles, animate)

if animate:
    plt.show()




"""
Tests

n = 100, num_trials = 100:
circles required for left-right = 40.15
circles required for area fill = 390.16


n = 100, num_trials = 1000:
circles required for left-right = 39.522
circles required for area fill = 389.025


n = 1000, num_trials = 10:
circles required for left-right = 354.5
circles required for area fill = 4488.4

n = 1000, num_trials = 10:
circles required for left-right = 347.3
circles required for area fill = 4506.6

n = 1000, num_trials = 10:
circles required for left-right = 362.2
circles required for area fill = 4457.0

n = 1000, num_trials = 100:
circles required for left-right = 371.12
circles required for area fill = 4399.5



"""
