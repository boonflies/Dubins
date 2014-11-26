#--------------
# Change Log:
#--------------
# Date: Oct 28, 2014
# Modification: #1 Plot equal axis function added
# -----------------------------------------------------

import time
from math import sqrt, cos, sin, atan
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D


import numpy as np

from Functions import Cylinder, Sphere, Spheres
from excel import excel_read, excel_write


plot_points = np.array([])
pi = 3.14

z_max = 20   # maximum altitude check
z_min = 1   # minimum altitude check
max_turning_angle = (3/float(4)) * pi   # maximum turning angle in radians check
delay_time = 1   # time for each waypoint computation check how to take this into consideration
velocity = 1  # velocity of the UAV c130heck
n = 1   #control the velocity of UAV - check how is this computed online
min_turn_radius = 1   # UAV minimum turning radius
k_angular_velocity = 0.2   # UAV angular velocity
shape = 'sphere'   # provide 'cylinder' or 'sphere' or 'scatter' or 'sphere1'
type_plot = 'none'   # provide 'plot' or 'animation' or 'none'

#Obstacle position
obstacle = [[15,5,5]] #check

threat = []   #variable to hold the obstacles found


flyable_min_dist = 3 #minimum distance between UAV and obstacle - check

#Creating a figure with 3D axes, labels and titles
fig = plt.figure()
fig.suptitle('Animation')
fig.canvas.set_window_title('Tracking animation')
ax = plt.axes(projection = '3d')
ax.set_xlabel("x axis")
ax.set_ylabel("y_axis")
ax.set_zlabel("z_axis")


def figure_close():
    plt.close('all')

# Plot the obstacle on the axes
def draw_obstacle(threat):
    for item in obstacle:
        x_obstacle = item[0]
        y_obstacle = item[1]
        z_obstacle = item[2]
        if shape == 'sphere':
            r = 1.5
            (xo, yo, zo) = Sphere(x_obstacle, y_obstacle, z_obstacle, r)
            if item in threat:
                ax.plot_wireframe(xo, yo, zo, color = "g")
            else:
                ax.plot_wireframe(xo, yo, zo, color = "r")
        elif shape == 'cylinder':
            r = np.linspace(2,.5,100)
            n = 20
            (xo, yo, zo) = Cylinder(x_obstacle, y_obstacle, z_obstacle, r, n)
            if item in threat:
                ax.plot_wireframe(xo, yo, zo, color = "g")
            else:
                ax.plot_wireframe(xo, yo, zo, color = "r")
        elif shape == 'scatter':
            if item in threat:
                ax.scatter(x_obstacle, y_obstacle, z_obstacle, color = "g", s = pi * (25 ** 2))
            else:
                ax.scatter(x_obstacle, y_obstacle, z_obstacle, color = "r", s = pi * (125 ** 2))
        elif shape == 'Sphere1':
            r = 5
            (x, y, z) = Spheres(x_obstacle, y_obstacle, z_obstacle, r)
            ax.plot_surface(x, y, z, rstride=4, cstride=4, color='b')





# Determine UAV's distance to next waypoint based on the change in velocity (parameter 'n')
def Calc_next_waypoint_distance(): #check
    max_distance_in_certain_velocity = Calc_max_distance()
    return n * max_distance_in_certain_velocity

# Determine the maximum distance the UAV can travel with the current velocity
def Calc_max_distance(): #check
    return velocity * delay_time


class UAV_Calc(object):

    def __init__(self, x_UAVs, y_UAVs, z_UAVs, bearing_UAVs, heading_UAVs, x_targets, y_targets, z_targets, bearing_targets, heading_targets):

        # considering the UAV
        self.x_UAV = [x_UAVs]
        self.y_UAV = [y_UAVs]
        self.z_UAV = [z_UAVs]
        self.bearing_UAV = [bearing_UAVs]
        self.heading_UAV = [heading_UAVs]
        position_UAV = [x_UAVs, y_UAVs, z_UAVs, bearing_UAVs, heading_UAVs]
        self.position_UAV = [position_UAV]

        # considering the target
        self.x_target = [x_targets]
        self.y_target = [y_targets]
        self.z_target = [z_targets]
        self.bearing_target = [bearing_targets]
        self.heading_target = [heading_targets]
        position_target = [x_targets, y_targets, z_targets, bearing_targets, heading_targets]
        self.position_target = [position_target]

        # different distances
        self.distance_UAV_to_target = 0
        self.distance_2D_slope = 0   # distance between UAV and target in xy plane

        # variable related to obstacles
        self.distance_to_obstacle_2D = 0   # distance to obstacle in xy plane
        self.distance_to_obstacle = 0   # distance to obstacle in xyz axes
        self.current_obstacle = 0 #value of current obstacle

        # FOR DUBINS CIRCLE
        # primary circle coordinates in xy
        self.x_primary_circle = 0
        self.y_primary_circle = 0

        # tangent exit points
        self.x_tangent_exit_one = 0
        self.x_tangent_exit_two = 0
        self.y_tangent_exit_one = 0
        self.y_tangent_exit_one = 0

        # The next waypoint for UAV after completing Dubins
        self.x_next_waypoint_UAV_one = 0
        self.x_next_waypoint_UAV_two = 0
        self.y_next_waypoint_UAV_one = 0
        self.y_next_waypoint_UAV_two = 0

        self.target_count = 1
        self.target_numbers = len(Target_points) - 1   # Actual minus 1

        self.distance_obstacle = []
        self.algorithm = ['Given']

    # Distance to target in xyz axes
    def calc_dist_to_target(self): #NOT USED check

        self.distance_UAV_to_target = sqrt( ( (self.x_UAV[-1] - self.x_target[-1])**2) + ( (self.y_UAV[-1] - self.y_target[-1])**2) + ( (self.z_UAV[-1] - self.z_target[-1])**2) )
        return self.distance_UAV_to_target


    # function to calculate distance to target - used to fill excel column
    def calc_dist_to_target_total(self):
        distance = []
        for i in range(len(self.x_target)):
            distance.append(sqrt( ( (self.x_UAV[i] - self.x_target[i])**2) +
                            ( (self.y_UAV[i] - self.y_target[i])**2) + ( (self.z_UAV[i] - self.z_target[i])**2) ) )
        return distance

    # Distacne to target in xy plane
    def calc_dist_2D_slope(self):
        self.distance_2D_slope = sqrt( ( (self.x_UAV[-1] - self.x_target[-1])**2 ) + ( (self.y_UAV[-1] - self.y_target[-1])**2) )
        return self.distance_2D_slope


    # Distance to obstacle in xy plane
    def calc_dist_to_obstacle_2D(self, obstacle_x, obstacle_y):
        self.distance_to_obstacle_2D = sqrt( ( (self.x_UAV[-1] - obstacle_x)**2 ) + ( (self.y_UAV[-1] - obstacle_y)**2 ) )


    # Distance to obstacle in xyz axes
    def calc_dist_to_obstacle(self, obstacle_x, obstacle_y, obstacle_z):
        self.distance_to_obstacle = sqrt( ( (self.x_UAV[-1] - obstacle_x)**2 ) + ( (self.y_UAV[-1] - obstacle_y)**2 ) + ( (self.z_UAV[-1] - obstacle_z)**2 ) )
        return self.distance_to_obstacle



    # Heading of UAV and Target for LINEAR ALGORITHM
    def calc_heading(self):
        new_heading = atan ( abs(self.y_target[-1] - self.y_UAV[-1]) / abs(self.x_target[-1] - self.x_UAV[-1]) )
        if new_heading > max_turning_angle:
            new_heading = max_turning_angle

        self.heading_UAV.append(new_heading)


    # Bearing of UAV and target for LINEAR ALGORITHM
    def calc_bearing(self):
        self.calc_dist_2D_slope()
        new_bearing = atan ( ( abs(self.z_target[-1] - self.z_UAV[-1]) )  / self.distance_2D_slope )
        if new_bearing > max_turning_angle:
            new_bearing = max_turning_angle

        self.bearing_UAV.append(new_bearing)


    # Determine the next possible x position of UAV and Target for LINEAR ALGORITHM
    def next_x_UAV_waypoint(self):
        if self.x_UAV[-1] < self.x_target[-1]:
            next_x_waypoint = self.x_UAV[-1] + (Calc_next_waypoint_distance() * cos(self.heading_UAV[-1]))
        elif self.x_UAV[-1] > self.x_target[-1]:
            next_x_waypoint = self.x_UAV[-1] - (Calc_next_waypoint_distance() * cos(self.heading_UAV[-1]))
        else:
            next_x_waypoint = self.x_UAV[-1]

        self.x_UAV.append(next_x_waypoint)


    # Determine the next possible y position of UAV and Target for LINEAR ALGORITHM
    def next_y_UAV_waypoint(self):
        if self.y_UAV[-1] < self.y_target[-1]:
            next_y_waypoint = self.y_UAV[-1] + (Calc_next_waypoint_distance() * sin(self.heading_UAV[-1]))
        elif self.y_UAV[-1] > self.y_target[-1]:
            next_y_waypoint = self.y_UAV[-1] - (Calc_next_waypoint_distance() * sin(self.heading_UAV[-1]))
        else:
            next_y_waypoint = self.y_UAV[-1]

        self.y_UAV.append(next_y_waypoint)


    # Determine the next possible z position of UAV and Target for LINEAR ALGORITHM
    def next_z_UAV_waypoint(self):
        if self.z_UAV[-1] < self.z_target[-1]:
            next_z_waypoint = self.z_UAV[-1] + (Calc_next_waypoint_distance() * sin(self.bearing_UAV[-1]))
        elif self.z_UAV[-1] > self.z_target[-1]:
            next_z_waypoint = self.z_UAV[-1] - (Calc_next_waypoint_distance() * sin(self.bearing_UAV[-1]))
        else:
            next_z_waypoint = self.z_UAV[-1]

        if next_z_waypoint > z_max:
            next_z_waypoint = z_max

        if next_z_waypoint < z_min:
            next_z_waypoint = z_min

        self.z_UAV.append(next_z_waypoint)


    # Determine the next UAV position using LINEAR ALGORITHM
    def compute_UAV_position(self):
        self.next_x_UAV_waypoint()
        self.next_y_UAV_waypoint()
        self.next_z_UAV_waypoint()
        self.calc_heading()
        self.calc_bearing()


    # Update next UAV position
    def update_UAV_position(self):
        new_position_UAV = [self.x_UAV[-1], self.y_UAV[-1], self.z_UAV[-1], self.bearing_UAV[-1], self.heading_UAV[-1]]
        self.position_UAV.append(new_position_UAV)


    # Determine the next Target position using LINEAR ALGORITHM
    def target_position(self):
        self.x_target.append(Target_x[self.target_count])
        self.y_target.append(Target_y[self.target_count])
        self.z_target.append(Target_z[self.target_count])
        self.heading_target.append(Target_heading[self.target_count])
        self.bearing_target.append(Target_z[self.target_count])

        if self.target_count < self.target_numbers:    # update from excel if the position is available in excel (so update the count)
            self.target_count = self.target_count + 1
        else:   # update the last given position in excel if new positions are not available (so don't update the count)
            pass

        #  Update next Target position
        new_position_target = [self.x_target[-1], self.y_target[-1], self.z_target[-1], self.bearing_target[-1], self.heading_target[-1]]
        self.position_target.append(new_position_target)


    # Linear Algorithm computation
    def linear_algorithm(self):

        while self.check_obstacle() and self.calc_dist_to_target() > 1:   # if no obstacle exists continue with linear algorithm
            self.compute_UAV_position()   # Calculate next position of UAV
            self.update_UAV_position()   # Update next position of UAV
            self.target_position()   # Calculate next position of target
            self.algorithm.append('linear')

            if len(self.x_UAV) > self.target_numbers:
                break


    def check_obstacle(self):
        for item in obstacle:
            x_obstacle = item[0]
            y_obstacle = item[1]
            z_obstacle = item[2]
            self.calc_dist_to_obstacle(x_obstacle, y_obstacle, z_obstacle)   # Distance between UAV and obstacle
            self.distance_obstacle.append(self.distance_to_obstacle)


            if self.distance_to_obstacle < flyable_min_dist:   # if obstacle is within the minimum flyable distance
                self.current_obstacle = [x_obstacle, y_obstacle, z_obstacle]
                #Remove the previous entries when obstacle is detected


                if self.current_obstacle not in threat:   # add the newly found obstacle to the list of threats
                    threat.append(self.current_obstacle)

                return 0   # If obstacle exists
                break
        return 1   # if obstacle does not exist


    # ---------------------------------------------------------------------------------------------------------------------------
    #Functions for Dubin's circle
    # ---------------------------------------------------------------------------------------------------------------------------

    #Orientation angle between secondary circle and modified Dubins start coordinate
    def orien_sec_cir_with_start_gamma(self):
        return atan(abs(self.current_obstacle[1] - self.y_UAV[-1]) / abs(self.current_obstacle[0] - self.x_UAV[-1]))

    #Orientation angle between primary circle and secondary circle
    def orien_pri_cir_with_sec_cir(self):
        return atan(abs(self.current_obstacle[1] - self.y_primary_circle) / abs(self.current_obstacle[0] - self.x_primary_circle))


    #Centre coordinate of primary circle for DUBINS
    def primary_circle_centre(self):
        self.x_primary_circle = self.x_UAV[-1] + (min_turn_radius * sin((pi/2) - self.orien_sec_cir_with_start_gamma()))
        self.y_primary_circle = self.y_UAV[-1] + (min_turn_radius * cos((pi/2) - self.orien_sec_cir_with_start_gamma()))


    #Tangent exit points for DUBINS
    def tangent_exit_pt(self):
        self.x_tangent_exit_one = self.current_obstacle[0] + flyable_min_dist * cos((pi/2) - self.orien_pri_cir_with_sec_cir())
        self.x_tangent_exit_two = self.current_obstacle[0] - flyable_min_dist * cos((pi/2) - self.orien_pri_cir_with_sec_cir())
        self.y_tangent_exit_one = self.current_obstacle[1] + flyable_min_dist * sin((pi/2) - self.orien_pri_cir_with_sec_cir())
        self.y_tangent_exit_two = self.current_obstacle[1] - flyable_min_dist * sin((pi/2) - self.orien_pri_cir_with_sec_cir())


    #safety radius of obstacle for DUBINS
    def safety_radius(self):
        return self.orien_pri_cir_with_sec_cir() + k_angular_velocity


    #next waypoint of UAV after DUBIN"S safety path
    def next_waypoint_after_Dubins_UAV(self):
        self.x_next_waypoint_UAV_one = self.current_obstacle[0] + flyable_min_dist * cos((pi/2) + self.safety_radius())
        self.x_next_waypoint_UAV_two = self.current_obstacle[0] - flyable_min_dist * cos((pi/2) + self.safety_radius())
        self.y_next_waypoint_UAV_one = self.current_obstacle[1] + flyable_min_dist * sin((pi/2) + self.safety_radius())
        self.y_next_waypoint_UAV_two = self.current_obstacle[1] - flyable_min_dist * sin((pi/2) + self.safety_radius())

        self.x_UAV.append(self.x_next_waypoint_UAV_one)
        self.y_UAV.append(self.y_next_waypoint_UAV_one)

        # To find next z waypoint afert DUBIN's safety path
        self.next_z_UAV_waypoint()

        self.calc_heading()
        self.calc_bearing()

        self.update_UAV_position()

    # Computing Dubin's algorithm
    def dubins(self):
        # self.x_UAV.pop()
        # self.y_UAV.pop()
        # self.z_UAV.pop()
        # self.x_target.pop()
        # self.y_target.pop()
        # self.z_target.pop()
        # self.position_UAV.pop()
        # self.position_target.pop()
        self.tangent_exit_pt()
        self.next_waypoint_after_Dubins_UAV() # computing and updating UAV position after following Dubin's safety path
        self.algorithm.append('dubins')


    # The entire algorithm (Linear Algorithm plus Dubin's Algorithm)
    def modified_dubins(self):
        i = 0
        while self.calc_dist_to_target() > 1:
            self.linear_algorithm()
            while not self.check_obstacle():
                self.dubins()
                self.target_position()   # update Target position

            i += 1


    #used if only plotting is necessary without animation
    def plot_UAV_path(self):
        draw_obstacle(threat)

        line1 = ax.plot(self.x_UAV, self.y_UAV, self.z_UAV, '-.b')
        line2 = ax.plot(self.x_target, self.y_target, self.z_target, '-or')
        self.axisEqual3D(ax) # make the axis of equal length
        ax.autoscale_view()
        ax.margins(0.5)

        #to make line opaque
        # line1[0].set_alpha(1)
        # line2[0].set_alpha(1)

        plt.show()


    def animate_UAV_path(self, i):
        draw_obstacle(threat)
        x = self.x_UAV[0:i]
        y = self.y_UAV[0:i]
        z = self.z_UAV[0:i]
        x1 = self.x_target[0:i]
        y1 = self.y_target[0:i]
        z1 = self.z_target[0:i]
        ax.plot(x,y,z, '-.b')
        ax.plot(x1, y1, z1, '-or')

    def plot_points(self):
        return np.array([['x_UAV', 'y_UAV', 'z_UAV', 'x_target', 'y_target','z_target', 'Target_x', 'Target_y', 'Target_z'],
                    self.x_UAV, self.y_UAV, self.z_UAV, self.x_target, self.y_target, self.z_target])

    def axisEqual3D(self, ax):
        extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:,1] - extents[:,0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

Target_points = excel_read()
Target_x = []
Target_y = []
Target_z = []
Target_heading = []
Target_bearing = []

def main(*args):
    global plot_points
    for i in range(len(Target_points)):
        Target_x.append(Target_points[i][0])
        Target_y.append(Target_points[i][1])
        Target_z.append(Target_points[i][2])
        Target_heading.append(Target_points[i][3])
        Target_heading.append(Target_points[i][4])


    # Declaring a UAV with inital and final position for testing
    UAV_one = UAV_Calc(30, 30, 20, 0.5, 0.5, Target_points[0][0], Target_points[0][1], Target_points[0][2], Target_points[0][3], Target_points[0][4])


    UAV_one.modified_dubins()

    # Update the UAV and target positions in Excel
    excel_write(UAV_one.x_UAV, UAV_one.y_UAV, UAV_one.z_UAV, UAV_one.heading_UAV, UAV_one.bearing_UAV,
        UAV_one.x_target, UAV_one.y_target, UAV_one.z_target, UAV_one.heading_target, UAV_one.bearing_target,
        UAV_one.calc_dist_to_target_total(), UAV_one.distance_obstacle, UAV_one.algorithm)

    plot_points = UAV_one.plot_points()

    if type_plot == 'plot':
            UAV_one.plot_UAV_path()
    elif type_plot == 'animation':
        # Below two lines are required for Animation of plot
        ani = animation.FuncAnimation(fig, UAV_one.animate_UAV_path, interval = 1000)
        plt.show()
    elif type_plot == 'none':
        pass



    UAV_one.distance_obstacle.append('not considered')


##main(type_plot)



