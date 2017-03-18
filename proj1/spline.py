# -*- coding: utf-8 -*-

from PyQt5.QtGui import QVector3D

from .quaternion import Quaternion


def read_spec(path):
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
        assert num_splines == 1
        for _ in range(num_splines):
            num_ctrl_pts = int(next(data_lines))
            ani_time = float(next(data_lines))
            ctrl_pts = []
            rotations = []
            for _ in range(num_ctrl_pts):
                x, y, z = map(float, next(data_lines).split(', '))
                ctrl_pt = QVector3D(x, y, z)
                ctrl_pts.append(ctrl_pt)

                x_rot, y_rot, z_rot = map(float, next(data_lines).split(', '))
                rot = Quaternion.from_euler_angles(x_rot, y_rot, z_rot)
                rotations.append(rot)

            splines = []
            for spline_type in (CatmullRomSpline, UniformBSpline):
                splines.append(spline_type(ani_time, *ctrl_pts))

            return splines, rotations

class Spline(object):
    def __init__(self, ani_time, *ctrl_pts):
        self.ani_time = ani_time
        self.ctrl_pts = ctrl_pts

    def __repr__(self):
        return type(self).__name__ + '(' + repr(self.ani_time) + ''.join(', ' + repr(pt) for pt in self.ctrl_pts) + ')'

class CatmullRomSpline(Spline):
    def pos_at(self, t):
        # TODO: catmull-rom spline
        return QVector3D(0.0, 0.0, 0.0)

class UniformBSpline(Spline):
    def pos_at(self, t):
        # TODO: uniform b-spline
        return QVector3D(0.0, 0.0, 0.0)
