# -*- coding: utf-8 -*-

import os

from PyQt5.QtGui import QVector3D

from .quaternion import Quaternion


def read_spec(path, spline_type):
    with open(path, 'r') as f:
        def filter_lines(line):
            line = line.strip()
            if not line:
                return False
            if line.startswith('#'):
                return False
            return True
        data_lines = filter(filter_lines, f)
        data_lines = iter(data_lines)

        num_splines = int(next(data_lines))
        splines = []
        for _ in range(num_splines):
            num_ctrl_pts = int(next(data_lines))
            ani_time = float(next(data_lines))
            ctrl_pts = []
            print(ani_time)
            for _ in range(num_ctrl_pts):
                x, y, z = map(float, next(data_lines).split(', '))
                pt = QVector3D(x, y, z)
                print(pt)
                x_rot, y_rot, z_rot = map(float, next(data_lines).split(', '))
                rot = Quaternion.from_euler_angles(x_rot, y_rot, z_rot)
                print(rot)
                ctrl_pts.append((pt, rot))
            splines.append(spline_type(ani_time, *ctrl_pts))
    return splines

class Spline(object):
    def __init__(self, ani_time, *ctrl_pts):
        self.ani_time = ani_time
        self.ctrl_pts = ctrl_pts

class CatmullRomSpline(Spline):
    pass

class UniformBSpline(Spline):
    pass
