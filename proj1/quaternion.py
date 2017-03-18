# -*- coding: utf-8 -*-

import numbers
import math

from PyQt5.QtGui import QVector3D, QMatrix3x3, QMatrix4x4


class Quaternion(object):
    @staticmethod
    def slerp(rotations, t):
        # TODO: slerp rotations
        return Quaternion()

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
        q_r = self.s
        q_i = self.x
        q_j = self.y
        q_k = self.z
        m = QMatrix3x3(
            1 - 2 * (q_j * q_j + q_k * q_k),     2 * (q_i * q_j - q_k * q_r),     2 * (q_i * q_k + q_j * q_r),
                2 * (q_i * q_j + q_k * q_r), 1 - 2 * (q_i * q_i + q_k * q_k),     2 * (q_j * q_k - q_i * q_r),
                2 * (q_i * q_k - q_j * q_r),     2 * (q_j * q_k + q_i * q_r), 1 - 2 * (q_i * q_i + q_j * q_j))
        m.optimize()
        return m

    @property
    def mat4x4(self):
        # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
        q_r = self.s
        q_i = self.x
        q_j = self.y
        q_k = self.z
        m = QMatrix4x4(
            1 - 2 * (q_j * q_j + q_k * q_k),     2 * (q_i * q_j - q_k * q_r),     2 * (q_i * q_k + q_j * q_r), 0,
                2 * (q_i * q_j + q_k * q_r), 1 - 2 * (q_i * q_i + q_k * q_k),     2 * (q_j * q_k - q_i * q_r), 0,
                2 * (q_i * q_k - q_j * q_r),     2 * (q_j * q_k + q_i * q_r), 1 - 2 * (q_i * q_i + q_j * q_j), 0,
                                          0,                               0,                               0, 1)
        m.optimize()
        return m

    def __str__(self):
        return '<' + str(self.s) + ', (' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')>'

    def __repr__(self):
        return 'Quaternion(' + repr(self.s) + ', ' + repr(self.x) + ', ' + repr(self.y) + ', ' + repr(self.z) + ')'


if __name__ == '__main__':
    # TODO: unit tests
    exit(0)
