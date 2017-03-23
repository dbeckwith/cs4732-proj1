# -*- coding: utf-8 -*-

import numbers
import math

from PyQt5.QtGui import QVector3D, QMatrix3x3, QMatrix4x4


class Quaternion(object):
    @staticmethod
    def slerp(t, *rotations):
        assert len(rotations) >= 2
        if len(rotations) == 2:
            q1, q2 = rotations
            if t == 0.5:
                return (q1 + q2).normalized
            angle = math.acos(q1.dot(q2))
            sin_angle = math.sin(angle)
            if sin_angle == 0.0:
                return q1
            return (math.sin((1 - t) * angle) / sin_angle * q1 + math.sin(t * angle) / sin_angle * q2).normalized
        else:
            if t < 0:
                return rotations[0]
            if t >= 1:
                return rotations[-1]
            i, t = divmod(t * (len(rotations) - 1), 1)
            i = int(i)
            return Quaternion.slerp(t, rotations[i], rotations[i + 1])

    def __init__(self, s=1, x=0, y=0, z=0):
        self.s = s
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_angle_axis(t, x, y, z):
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        sin_t2 = math.sin(t / 2)
        return Quaternion(
            math.cos(t / 2),
            sin_t2 * x,
            sin_t2 * y,
            sin_t2 * z)

    @staticmethod
    def from_euler_angles(t_x, t_y, t_z):
        """
        roll, pitch, yaw
        """
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        sx2 = math.sin(t_x / 2)
        cx2 = math.cos(t_x / 2)
        sy2 = math.sin(t_y / 2)
        cy2 = math.cos(t_y / 2)
        sz2 = math.sin(t_z / 2)
        cz2 = math.cos(t_z / 2)
        return Quaternion(
            cx2 * cy2 * cz2 + sx2 * sy2 * sz2,
            sx2 * cy2 * cz2 - cx2 * sy2 * sz2,
            cx2 * sy2 * cz2 + sx2 * cy2 * sz2,
            cx2 * cy2 * sz2 - sx2 * sy2 * cz2)

    @property
    def v(self):
        return QVector3D(self.x, self.y, self.z)

    def __add__(self, other):
        return Quaternion(self.s + other.s, self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Quaternion(self.s - other.s, self.x - other.x, self.y - other.y, self.z - other.z)

    def __pos__(self):
        return Quaternion(+self.s, +self.x, +self.y, +self.z)

    def __neg__(self):
        return Quaternion(-self.s, -self.x, -self.y, -self.z)

    def __abs__(self):
        return self.norm

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Quaternion(self.s * other, self.x * other, self.y * other, self.z * other)
        else:
            return Quaternion(
                self.s * other.s - self.x * other.x - self.y * other.y - self.z * other.z,
                self.s * other.x + other.s * self.x + self.y * other.z - self.z * other.y,
                self.s * other.y + other.s * self.y + self.z * other.x - self.x * other.z,
                self.s * other.z + other.s * self.z + self.x * other.y - self.y * other.x)

    def __rmul__(self, other):
        if isinstance(other, numbers.Number):
            return Quaternion(other * self.s, other * self.x, other * self.y, other * self.z)
        return NotImplemented

    def dot(self, other):
        return self.s * other.s + self.x * other.x + self.y * other.y + self.z * other.z

    @property
    def conjugate(self):
        return Quaternion(self.s, -self.x, -self.y, -self.z)

    @property
    def normsq(self):
        return self.s * self.s + self.x * self.x + self.y * self.y + self.z * self.z

    @property
    def norm(self):
        return math.sqrt(self.normsq)

    @property
    def normalized(self):
        return self / self.norm

    @property
    def reciprocal(self):
        return self.conjugate / self.normsq

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return Quaternion(self.s / other, self.x / other, self.y / other, self.z / other)
        else:
            return self * other.reciprocal

    @property
    def mat3x3(self):
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        s = self.s
        x = self.x
        y = self.y
        z = self.z
        m = QMatrix3x3(
            1 - 2 * (y * y + z * z),     2 * (x * y - s * z),     2 * (x * z + s * y),
                2 * (x * y + s * z), 1 - 2 * (x * x + z * z),     2 * (y * z - s * x),
                2 * (x * z - s * y),     2 * (y * z + s * x), 1 - 2 * (x * x + y * y))
        m.optimize()
        return m

    @property
    def mat4x4(self):
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        s = self.s
        x = self.x
        y = self.y
        z = self.z
        m = QMatrix4x4(
            1 - 2 * (y * y + z * z),     2 * (x * y - s * z),     2 * (x * z + s * y), 0,
                2 * (x * y + s * z), 1 - 2 * (x * x + z * z),     2 * (y * z - s * x), 0,
                2 * (x * z - s * y),     2 * (y * z + s * x), 1 - 2 * (x * x + y * y), 0,
                                  0,                       0,                       0, 1)
        m.optimize()
        return m

    def __str__(self):
        return '<' + str(self.s) + ', (' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')>'

    def __repr__(self):
        return 'Quaternion(' + repr(self.s) + ', ' + repr(self.x) + ', ' + repr(self.y) + ', ' + repr(self.z) + ')'


if __name__ == '__main__':
    # TODO: unit tests
    exit(0)
