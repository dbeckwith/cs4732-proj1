#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math

from PyQt5 import QtCore, QtGui, QtWidgets, Qt3DCore, Qt3DRender, Qt3DExtras

from .animation import Animation
from . import util


class Proj1Ani(Animation):
    """
    Implements the spline animation.
    """

    def __init__(self, frame_rate, run_time):
        super().__init__('CS 4732 Project 1 by Daniel Beckwith', frame_rate, run_time)

        self.setup_scene(
            background_color=util.hsl(0, 0, 0),
            camera_position=QtGui.QVector3D(0.0, 0.0, -10.0),
            camera_lookat=QtGui.QVector3D(0.0, 0.0, 0.0))

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
    args = parser.parse_args()

    app = QtWidgets.QApplication([])

    ani = Proj1Ani(60, 10.0)
    ani.run()

    sys.exit(app.exec_())
