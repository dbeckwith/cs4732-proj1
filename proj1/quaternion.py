# -*- coding: utf-8 -*-

import numbers
import math

from PyQt5.QtGui import QVector3D


class Quaternion(object):
    def __init__(self, s=1, x=0, y=None, z=None):
        assert isinstance(s, numbers.Number)
        self.s = s
        if y is None and z is None:
            assert isinstance(x, QVector3D)
            self.v = x
        else:
            assert isinstance(x, numbers.Number)
            assert isinstance(y, numbers.Number)
            assert isinstance(z, numbers.Number)
            self.v = QVector3D(x, y, z)

    @property
    def x(self):
        return self.v.x()

    @x.setter
    def x(self, x):
        self.v.setX(x)

    @property
    def y(self):
        return self.v.y()

    @y.setter
    def y(self, y):
        self.v.setY(y)

    @property
    def z(self):
        return self.v.z()

    @z.setter
    def z(self, z):
        self.v.setZ(z)

    def __add__(self, other):
        return Quaternion(self.s + other.s, self.v + other.v)

    def __sub__(self, other):
        return Quaternion(self.s - other.s, self.v - other.v)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Quaternion(self.s * other, self.v * other)
        else:
            return Quaternion(
                self.s * other.s - QVector3D.dotProduct(self.v, other.v),
                self.s * other.v + other.s * self.v + QVector3D.crossProduct(self.v, other.v))

    @property
    def conjugate(self):
        return Quaternion(self.s, -self.v)

    @property
    def normsq(self):
        return self.s * self.s + self.v.lengthSquared()

    @property
    def norm(self):
        return math.sqrt(self.normsq)

    @property
    def reciprocal(self):
        return self.conjugate / self.normsq

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return Quaternion(self.s / other, self.v / other)
        else:
            return self * other.reciprocal
