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


# QUESTIONS:
# need to do rotation bezier smoothing?
# need to do automatic tangents for Catmull-Rom spline?
# need to do distance-based interpolation?


class Proj1Ani(Animation):
    """
    Implements the spline animation.
    """

    def __init__(self, spline_spec_path):
        self.splines, self.rotations = read_spline_spec(spline_spec_path)
        total_time = sum(spline.ani_time for spline in self.splines)

        super().__init__('CS 4732 Project 1 by Daniel Beckwith', 60.0, total_time)

        # TODO: position camera to include all spline points
        self.setup_scene(
            background_color=util.hsl(0, 0, 0),
            camera_position=QVector3D(0.0, 0.0, -10.0),
            camera_lookat=QVector3D(0.0, 0.0, 0.0))

        self.spline_end_times = itertools.accumulate(spline.ani_time for spline in self.splines)
        self.splines = iter(self.splines)
        self.curr_spline = None
        self.curr_spline_start_time = None
        self.curr_spline_end_time = None
        self._next_spline()

    def make_scene(self):
        self.cube_transform = self.add_rgb_cube(1.0, 1.0, 1.0)

    def _next_spline(self):
        try:
            self.curr_spline = next(self.splines)
            if self.curr_spline_end_time is None:
                self.curr_spline_start_time = 0
            else:
                self.curr_spline_start_time = self.curr_spline_end_time
            self.curr_spline_end_time = next(self.spline_end_times)
        except StopIteration:
            self.curr_spline = None
            self.curr_spline_start_time = None
            self.curr_spline_end_time = None

    def update(self, frame, t, dt):
        spline_t = util.lerp(t, self.curr_spline_start_time, self.curr_spline_end_time, 0, 1)

        pos = self.curr_spline.pos_at(spline_t)
        rot = Quaternion.slerp(spline_t, *self.rotations)

        xform = QMatrix4x4(rot.mat4x4)
        xform.translate(pos)
        self.cube_transform.setMatrix(xform)

        if t >= self.curr_spline_end_time:
            self._next_spline()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='proj1',
        description='Animates an object travelling along a spline.',
        epilog='Created by Daniel Beckwith for WPI CS 4732.')
    parser.add_argument('spline_spec')
    args = parser.parse_args()

    app = QApplication([])

    ani = Proj1Ani(args.spline_spec)
    ani.run()

    sys.exit(app.exec_())
