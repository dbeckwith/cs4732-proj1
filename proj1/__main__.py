#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import itertools

from PyQt5.QtGui import QVector3D, QMatrix4x4
from PyQt5.QtWidgets import QApplication

from .animation import Animation
from .quaternion import Quaternion
from .spline import read_spec as read_spline_spec
from .spline import CatmullRomSpline, UniformBSpline
from . import util


class Proj1Ani(Animation):
    """
    Implements the spline animation.
    """

    def __init__(self, spline_spec_path):
        # read in splines and get list of them and rotations
        self.splines, self.rotations = read_spline_spec(spline_spec_path)
        # total animation time is sum of each spline's animation time
        total_time = sum(spline.ani_time for spline in self.splines)

        super().__init__('CS 4732 Project 1 by Daniel Beckwith', 60.0, total_time)

        # determine extent of spline ctrl points for positioning camera
        spline_min = QVector3D(float('+inf'), float('+inf'), float('+inf'))
        spline_max = QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for spline in self.splines:
            for p in spline.ctrl_pts:
                if p.x() < spline_min.x():
                    spline_min.setX(p.x())
                if p.x() > spline_max.x():
                    spline_max.setX(p.x())
                if p.y() < spline_min.y():
                    spline_min.setY(p.y())
                if p.y() > spline_max.y():
                    spline_max.setY(p.y())
                if p.z() < spline_min.z():
                    spline_min.setZ(p.z())
                if p.z() > spline_max.z():
                    spline_max.setZ(p.z())
        spline_center = (spline_min + spline_max) / 2
        spline_extent = (spline_max - spline_min).length()

        # set up scene with camera covering all spline paths
        self.setup_scene(
            background_color=util.hsl(0, 0, 0),
            camera_position=spline_center + QVector3D(0.0, 0.0, -2.5 * spline_extent),
            camera_lookat=spline_center)

        # add a sphere marking each ctrl point of each spline
        for spline in self.splines:
            for p in spline.ctrl_pts:
                xform = self.add_sphere(0.2)
                xform.setTranslation(p)

        # iterator of the time when each spline animation ends
        self.spline_end_times = itertools.accumulate(spline.ani_time for spline in self.splines)
        # iterator of the splines
        self.splines = iter(self.splines)

        self.curr_spline = None
        self.curr_spline_start_time = None
        self.curr_spline_end_time = None
        self.spline_path = None

        self._next_spline()

    def make_scene(self):
        """
        Overriddes Animation.make_scene
        """
        # cube that will follow the splines
        self.cube_transform = self.add_rgb_cube(1.0, 1.0, 1.0)

        # add some lights
        self.add_light(QVector3D(-20.0, 20.0, -20.0), 1.0) # upper right key light
        self.add_light(QVector3D(20.0, 10.0, -20.0), 0.5) # upper left fill light

    def _next_spline(self):
        """
        Advances to the next spline to be animated.
        """
        try:
            # get the next spline
            self.curr_spline = next(self.splines)

            # the first start time is 0, otherwise it's the previous end time
            self.curr_spline_start_time = 0 if self.curr_spline_end_time is None else self.curr_spline_end_time

            # get the next end time
            self.curr_spline_end_time = next(self.spline_end_times)

            if self.spline_path is not None:
                # if had a spline path from before, remove it from the scene
                for p in self.spline_path:
                    # setting the parent to null deletes the object
                    p.setParent(None)

            # create a path in the scene along the current spline
            path_pts = []
            num_path_pts = int(self.curr_spline.ani_time * self.frame_rate) # number of frames in the spline's animation
            for i in range(num_path_pts):
                t = util.lerp(i, 0, num_path_pts, 0, 1)
                path_pts.append(self.curr_spline.pos_at(t))
            self.spline_path = self.add_path(*path_pts)
        except StopIteration:
            # reached the end of the splines iterator
            self.curr_spline = None
            self.curr_spline_start_time = None
            self.curr_spline_end_time = None
            self.spline_path = None

    def update(self, frame, t, dt):
        """
        Overriddes Animation.update
        """
        # go to the next spline if past end time
        if t >= self.curr_spline_end_time:
            self._next_spline()

        if self.curr_spline is not None:
            # lerp spline parameter from animation time
            spline_t = util.lerp(t, self.curr_spline_start_time, self.curr_spline_end_time, 0, 1)

            # get spline point
            pos = self.curr_spline.pos_at(spline_t)
            # slerp rotations
            rot = Quaternion.slerp(spline_t, *self.rotations)

            # build transformation matrix
            # start with rotation matrix
            xform = QMatrix4x4(rot.mat4x4)
            # set translation cells
            xform[0, 3] = pos.x()
            xform[1, 3] = pos.y()
            xform[2, 3] = pos.z()
            # transform cube
            self.cube_transform.setMatrix(xform)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='proj1',
        description='Animates an object travelling along a spline.',
        epilog='Created by Daniel Beckwith for WPI CS 4732.')
    parser.add_argument('spline_spec', help='Path to a text file containing the spline and rotation control points.')
    args = parser.parse_args()

    app = QApplication([])

    ani = Proj1Ani(args.spline_spec)
    ani.run()

    sys.exit(app.exec_())
