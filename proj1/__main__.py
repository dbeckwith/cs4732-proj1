#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math

from PyQt5.QtGui import QVector3D
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
        self.splines = read_spline_spec(spline_spec_path, CatmullRomSpline)
        run_time = 10.0

        super().__init__('CS 4732 Project 1 by Daniel Beckwith', 60.0, run_time)

        self.setup_scene(
            background_color=util.hsl(0, 0, 0),
            camera_position=QVector3D(0.0, 0.0, -10.0),
            camera_lookat=QVector3D(0.0, 0.0, 0.0))

    def make_scene(self):
        pass

    def update(self, frame, t, dt):
        pass

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
