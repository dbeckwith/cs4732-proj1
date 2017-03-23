# -*- coding: utf-8 -*-

from PyQt5.QtGui import QVector3D, QVector4D, QMatrix4x4

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
        if t < 0:
            return self.ctrl_pts[0]
        if t >= 1:
            return self.ctrl_pts[-1]
        i, t = divmod(t * (len(self.ctrl_pts) - 1), 1)
        i = int(i)
        M = QMatrix4x4(
            -1,  3, -3,  1,
             2, -5,  4, -1,
            -1,  0,  1,  0,
             0,  2,  0,  0) / 2
        p2 = self.ctrl_pts[i]
        p3 = self.ctrl_pts[i + 1]
        if i == 0:
            # starting auto tangents
            p4 = self.ctrl_pts[i + 2]
            tangent = (2 * p3 - p4 - p2) / 2
            p1 = p2 - tangent
        elif i == len(self.ctrl_pts) - 2:
            # ending auto tangents
            p1 = self.ctrl_pts[i - 1]
            tangent = (2 * p2 - p1 - p3) / 2
            p4 = p3 + tangent
        else:
            p1 = self.ctrl_pts[i - 1]
            p4 = self.ctrl_pts[i + 2]
        B = QMatrix4x4(
            p1.x(), p1.y(), p1.z(), 1,
            p2.x(), p2.y(), p2.z(), 1,
            p3.x(), p3.y(), p3.z(), 1,
            p4.x(), p4.y(), p4.z(), 1)
        U = QVector4D(t * t * t, t * t, t, 1)
        return QVector3D(U * M * B)

class UniformBSpline(Spline):
    def pos_at(self, t):
        # TODO: uniform b-spline
        return QVector3D(0.0, 0.0, 0.0)
