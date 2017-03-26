# -*- coding: utf-8 -*-

from PyQt5.QtGui import QVector3D, QVector4D, QMatrix4x4

from . import util
from .quaternion import Quaternion


def read_spec(path):
    """
    Function that reads the given spline text file and creates splines and rotations from it.

    Arguments:
        path: str, path to a text file containing the spline and rotation control points

    Returns:
        (splines, rotations) where:
            splines: list of Spline objects, each spline read
            rotations: list of Quaternion objects, each rotation read
    """
    with open(path, 'r') as f: # open file as read-only
        # filter function to only get lines with data
        def filter_lines(line):
            line = line.strip() # get rid of excess whitespace
            if not line: # empty line
                return False
            if line.startswith('#'): # comment line
                return False
            return True
        # get iterator of lines containing data
        data_lines = iter(filter(filter_lines, f))

        # read number of splines in the file
        num_splines = int(next(data_lines))
        # should only be one spline specification
        # not really sure why this is in the file
        # since having more than one doesn't really make sense...
        assert num_splines == 1
        # read each spline
        for _ in range(num_splines):
            # read the number of control points in this spline
            num_ctrl_pts = int(next(data_lines))
            # read the time that this spline is supposed to be animated for
            ani_time = float(next(data_lines))
            ctrl_pts = []
            rotations = []
            # read control points
            for _ in range(num_ctrl_pts):
                # read line, split by commas, convert to floats
                x, y, z = map(float, next(data_lines).split(', '))
                # add control point
                ctrl_pt = QVector3D(x, y, z)
                ctrl_pts.append(ctrl_pt)

                # read line, split by commas, convert to floats
                x_rot, y_rot, z_rot = map(float, next(data_lines).split(', '))
                # add rotation
                rot = Quaternion.from_euler_angles(x_rot, y_rot, z_rot)
                rotations.append(rot)

            # now make each kind of spline from the control points
            splines = []
            for spline_type in (CatmullRomSpline, UniformBSpline):
                splines.append(spline_type(ani_time, *ctrl_pts))

            return splines, rotations

class Spline(object):
    """
    Abstract class representing a parameterized spline.
    Specifically, a spline whose points can be represented by the following formula:
    P(t) = U^T M B
    where U = [t^3, t^2, t, 1]
    and B is a matrix containing the four control points used for each point
    See section B.5 in Computer Animation by Rick Parent, 3rd Edition
    """

    def __init__(self, ani_time, *ctrl_pts):
        """
        Creates a new spline.

        Arguments:
            ani_time: float, time in seconds to animate this spline for
            ctrl_pts: list of QVector3D's, control points defining the shape of the spline
        """
        self.ani_time = ani_time
        self.ctrl_pts = ctrl_pts

    def _get_ctrl_pts(self, i):
        """
        Abstract method. Gets the control points needed.
        """
        raise NotImplementedError()

    def pos_at(self, t):
        """
        Gets the position of the spline at the given value of the interpolation parameter.
        t should vary from 0 to 1

        Arguments:
            t: float, the interpolation parameter

        Returns:
            a QVector3D representing the position of this spline at the given value
        """
        # if t out of bounds, return the endpoints
        if t < 0:
            return self.ctrl_pts[0]
        if t >= 1:
            return self.ctrl_pts[-1]
        # scale t to be from (i_start) to (i_end from the end of the ctrl_pts list)
        t = util.lerp(t, 0, 1, self.i_start, len(self.ctrl_pts) + self.i_end)
        # get integer and fractional parts of this
        i = int(t)
        t %= 1
        # i is now the index of the first ctrl point to be used
        # t is the interpolation parameter

        # get control points, depends on spline implementation
        p1, p2, p3, p4 = self._get_ctrl_pts(i)
        B = QMatrix4x4(
            p1.x(), p1.y(), p1.z(), 1,
            p2.x(), p2.y(), p2.z(), 1,
            p3.x(), p3.y(), p3.z(), 1,
            p4.x(), p4.y(), p4.z(), 1)
        U = QVector4D(t * t * t, t * t, t, 1)
        # left-multiplying a QVector4D with a QMatrix4x4 uses the QVector4D as a 1x4 row vector.
        return QVector3D(U * (self.M * B))

    def __repr__(self):
        return type(self).__name__ + '(' + repr(self.ani_time) + ''.join(', ' + repr(pt) for pt in self.ctrl_pts) + ')'

class CatmullRomSpline(Spline):
    """
    Implementation of a Catmull-Rom Spline.
    """

    # M-matrix determines interpolation weights
    M = QMatrix4x4(
        -1,  3, -3,  1,
         2, -5,  4, -1,
        -1,  0,  1,  0,
         0,  2,  0,  0) / 2
    # control points indicies start at 0
    i_start = 0
    # and go until the second-to-last
    i_end = -1

    def _get_ctrl_pts(self, i):
        """
        Overrides Spline._get_ctrl_pts
        """
        # middle two control points are always the same
        p2 = self.ctrl_pts[i]
        p3 = self.ctrl_pts[i + 1]
        if i == 0:
            # if at the first set of control points,
            # need to calculate starting auto tangents
            p4 = self.ctrl_pts[i + 2]
            tangent = (2 * p3 - p4 - p2) / 2
            p1 = p2 - tangent
        elif i == len(self.ctrl_pts) - 2:
            # if at the last set of control points,
            # need to calculate ending auto tangents
            p1 = self.ctrl_pts[i - 1]
            tangent = (2 * p2 - p1 - p3) / 2
            p4 = p3 + tangent
        else:
            # otherwise, just use the normal control points
            p1 = self.ctrl_pts[i - 1]
            p4 = self.ctrl_pts[i + 2]
        return p1, p2, p3, p4

class UniformBSpline(Spline):
    """
    Implementation of a Uniform B-Spline.
    """

    # M-matrix determines interpolation weights
    M = QMatrix4x4(
        -1,  3, -3,  1,
         3, -6,  3,  0,
        -3,  0,  3,  0,
         1,  4,  1,  0) / 6
    # control points indicies start at 0
    i_start = 0
    # and go until the fourth-to-last
    i_end = -3

    def _get_ctrl_pts(self, i):
        """
        Overrides Spline._get_ctrl_pts
        """
        # control points for this are just the four points starting at each index
        return self.ctrl_pts[i : i + 4]
