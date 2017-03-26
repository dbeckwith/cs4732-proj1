# -*- coding: utf-8 -*-

import numbers
import math

from PyQt5.QtGui import QVector3D, QMatrix3x3, QMatrix4x4


class Quaternion(object):
    """
    Class representing a quaternion-based rotation.
    """

    @staticmethod
    def slerp(t, *rotations):
        """
        Calculates a spherical linear interpolation between the quaternions given.
        A t-value of 0 gives the first quaternion, and a t-value of 1 gives the last quaternion.

        Arguments:
            t: float, interpolation parameter
            rotations: list of Quaternion's, the quaternion rotations to interpolate
        """
        # must have at least 2
        assert len(rotations) >= 2
        if len(rotations) == 2:
            # base case, slerp between two quaternions
            q1, q2 = rotations
            dot = q1.dot(q2)
            if dot == 1.0 or dot == -1.0:
                # quaternions are the same, no interpolation possible
                return q1
            elif dot < 0:
                # -q2 and q2 represent the same rotation,
                # so if -q2 is closer to q1, use that
                # they are closer if q1 faces away from q2,
                # meaning their dot product is negative
                q2 = -q2
                dot = -dot
            if t == 0.5:
                # simple formula for case when t is 1/2
                return (q1 + q2).normalized
            angle = math.acos(dot)
            return (math.sin((1 - t) * angle) * q1 + math.sin(t * angle) * q2) / math.sin(angle)
        else:
            # have more than 2 rotations
            # need to find the two that t is between

            # if t out of bounds, return the endpoints
            if t < 0:
                return rotations[0]
            if t >= 1:
                return rotations[-1]
            # scale t to be from 0 to the second-to-last rotation
            t *= len(rotations) - 1
            # get integer and fractional parts of this
            i = int(t)
            t %= 1
            # i is now the index of the first rotation
            # t is the interpolation parameter between them
            return Quaternion.slerp(t, rotations[i], rotations[i + 1])

    def __init__(self, s=1, x=0, y=0, z=0):
        """
        Creates a new Quaternion with the given components.

        Arguments:
            s: float, the scalar value of the quaternion
            x: float, the x-component of the vector part of the quaternion
            y: float, the y-component of the vector part of the quaternion
            z: float, the z-component of the vector part of the quaternion
        """
        self.s = s
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_angle_axis(t, x, y, z):
        """
        Converts a rotation represented by a an angle around a given axis to a quaternion.
        The axis must be normalized.

        Arguments:
            t: float, the angle in radians to rotate around the axis
            x: float, the x-component of the axis
            y: float, the y-component of the axis
            z: float, the z-component of the axis

        Returns:
            a Quaternion representing the same rotation
        """
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
        Converts a rotation represented by a set of Euler angles to a quaternion.

        Arguments:
            t_x: float, the angle in radians to rotate around the x-axis, also known as roll
            t_y: float, the angle in radians to rotate around the y-axis, also known as pitch
            t_z: float, the angle in radians to rotate around the z-axis, also known as yaw

        Returns:
            a Quaternion representing the same rotation
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
        """
        Gets the vector part of the quaternion as a QVector3D.
        """
        return QVector3D(self.x, self.y, self.z)

    def __add__(self, other):
        """
        Adds this quaternion to another.
        """
        return Quaternion(self.s + other.s, self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """
        Subtracts another quaternion from this.
        """
        return Quaternion(self.s - other.s, self.x - other.x, self.y - other.y, self.z - other.z)

    def __pos__(self):
        return Quaternion(+self.s, +self.x, +self.y, +self.z)

    def __neg__(self):
        """
        Additive inverse, or negative, of this quaternion.
        """
        return Quaternion(-self.s, -self.x, -self.y, -self.z)

    def __abs__(self):
        """
        Absolute value, or norm, of this quaternion.
        """
        return self.norm

    def __mul__(self, other):
        """
        Multiplies this quaternion by another quaternion or a scalar.
        """
        if isinstance(other, numbers.Number):
            # scalar multiplication
            return Quaternion(self.s * other, self.x * other, self.y * other, self.z * other)
        else:
            # quaternion multiplication
            return Quaternion(
                self.s * other.s - self.x * other.x - self.y * other.y - self.z * other.z,
                self.s * other.x + other.s * self.x + self.y * other.z - self.z * other.y,
                self.s * other.y + other.s * self.y + self.z * other.x - self.x * other.z,
                self.s * other.z + other.s * self.z + self.x * other.y - self.y * other.x)

    def __rmul__(self, other):
        """
        Right-multiply. Used in the expression x * q when x is a number and q is a quaternion.
        """
        if isinstance(other, numbers.Number):
            return Quaternion(other * self.s, other * self.x, other * self.y, other * self.z)
        return NotImplemented

    def dot(self, other):
        """
        Computes the dot-product of this quaternion with another.
        """
        return self.s * other.s + self.x * other.x + self.y * other.y + self.z * other.z

    @property
    def conjugate(self):
        """
        Computes the conjugate of this quaternion.
        """
        return Quaternion(self.s, -self.x, -self.y, -self.z)

    @property
    def normsq(self):
        """
        Computes the square of the norm of this quaternion.
        """
        return self.s * self.s + self.x * self.x + self.y * self.y + self.z * self.z

    @property
    def norm(self):
        """
        Computes the norm of this quaternion.
        """
        return math.sqrt(self.normsq)

    @property
    def normalized(self):
        """
        Returns a normalized version of this quaternion with norm equal to 1.
        """
        return self / self.norm

    @property
    def reciprocal(self):
        """
        Computes the multiplicative inverse, or reciprocal, of this quaternion.
        """
        return self.conjugate / self.normsq

    def __truediv__(self, other):
        """
        Divides this quaternion by another quaternion or a scalar.
        """
        if isinstance(other, numbers.Number):
            # scalar division
            return Quaternion(self.s / other, self.x / other, self.y / other, self.z / other)
        else:
            # quaternion division
            return self * other.reciprocal

    @property
    def mat3x3(self):
        """
        Converts this quaternion to a 3x3 rotation matrix.
        """
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
        """
        Converts this quaternion to a 4x4 rotation matrix.
        """
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
