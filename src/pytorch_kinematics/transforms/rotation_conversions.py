# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

import functools
from typing import Optional
from warnings import warn

import torch
import torch.nn.functional as F

"""
The transformation matrices returned from the functions in this file assume
the points on which the transformation will be applied are column vectors.
i.e. the R matrix is structured as

    R = [
            [Rxx, Rxy, Rxz],
            [Ryx, Ryy, Ryz],
            [Rzx, Rzy, Rzz],
        ]  # (3, 3)

This matrix can be applied to column vectors by post multiplication
by the points e.g.

    points = [[0], [1], [2]]  # (3 x 1) xyz coordinates of a point
    transformed_points = R * points

To apply the same matrix to points which are row vectors, the R matrix
can be transposed and pre multiplied by the points:

e.g.
    points = [[0, 1, 2]]  # (1 x 3) xyz coordinates of a point
    transformed_points = points * R.transpose(1, 0)
"""


def xyzw_to_wxyz(quaternions):
    pass


def wxyz_to_xyzw(quaternions):
    pass


def quaternion_to_matrix(quaternions):
    """
    Convert rotations given as quaternions to rotation matrices.

    Args:
        quaternions: quaternions with real part first,
            as tensor of shape (..., 4).

    Returns:
        Rotation matrices as tensor of shape (..., 3, 3).
    """
    pass


def _copysign(a, b):
    """
    Return a tensor where each element has the absolute value taken from the,
    corresponding element of a, with sign taken from the corresponding
    element of b. This is like the standard copysign floating-point operation,
    but is not careful about negative 0 and NaN.

    Args:
        a: source tensor.
        b: tensor whose signs will be used, of the same shape as a.

    Returns:
        Tensor of the same shape as a with the signs of b.
    """
    pass


def _sqrt_positive_part(x):
    """
    Returns torch.sqrt(torch.max(0, x))
    but with a zero subgradient where x is 0.
    """
    pass


def matrix_to_quaternion(matrix):
    """
    Convert rotations given as rotation matrices to quaternions.

    Args:
        matrix: Rotation matrices as tensor of shape (..., 3, 3).

    Returns:
        quaternions with real part first, as tensor of shape (..., 4). as w,x,y,z
    """
    pass


def _axis_angle_rotation(axis: str, angle):
    """
    Return the rotation matrices for one of the rotations about an axis
    of which Euler angles describe, for each value of the angle given.

    Args:
        axis: Axis label "X" or "Y or "Z".
        angle: any shape tensor of Euler angles in radians

    Returns:
        Rotation matrices as tensor of shape (..., 3, 3).
    """
    pass


def euler_angles_to_matrix(euler_angles, convention: str):
    """
    Convert rotations given as Euler angles in radians to rotation matrices.

    Args:
        euler_angles: Euler angles in radians as tensor of shape (..., 3).
        convention: Convention string of three uppercase letters from
            {"X", "Y", and "Z"}.

    Returns:
        Rotation matrices as tensor of shape (..., 3, 3).
    """
    pass


def _angle_from_tan(
        axis: str, other_axis: str, data, horizontal: bool, tait_bryan: bool
):
    """
    Extract the first or third Euler angle from the two members of
    the matrix which are positive constant times its sine and cosine.

    Args:
        axis: Axis label "X" or "Y or "Z" for the angle we are finding.
        other_axis: Axis label "X" or "Y or "Z" for the middle axis in the
            convention.
        data: Rotation matrices as tensor of shape (..., 3, 3).
        horizontal: Whether we are looking for the angle for the third axis,
            which means the relevant entries are in the same row of the
            rotation matrix. If not, they are in the same column.
        tait_bryan: Whether the first and third axes in the convention differ.

    Returns:
        Euler Angles in radians for each matrix in data as a tensor
        of shape (...).
    """
    pass


def _index_from_letter(letter: str):
    pass


def matrix_to_euler_angles(matrix, convention: str):
    """
    Convert rotations given as rotation matrices to Euler angles in radians.

    Args:
        matrix: Rotation matrices as tensor of shape (..., 3, 3).
        convention: Convention string of three uppercase letters.

    Returns:
        Euler angles in radians as tensor of shape (..., 3).
    """
    pass


def random_quaternions(
        n: int, dtype: Optional[torch.dtype] = None, device=None, requires_grad=False
):
    """
    Generate random quaternions representing rotations,
    i.e. versors with nonnegative real part.

    Args:
        n: Number of quaternions in a batch to return.
        dtype: Type to return.
        device: Desired device of returned tensor. Default:
            uses the current device for the default tensor type.
        requires_grad: Whether the resulting tensor should have the gradient
            flag set.

    Returns:
        Quaternions as tensor of shape (N, 4).
    """
    pass


def random_rotations(
        n: int, dtype: Optional[torch.dtype] = None, device=None, requires_grad=False
):
    """
    Generate random rotations as 3x3 rotation matrices.

    Args:
        n: Number of rotation matrices in a batch to return.
        dtype: Type to return.
        device: Device of returned tensor. Default: if None,
            uses the current device for the default tensor type.
        requires_grad: Whether the resulting tensor should have the gradient
            flag set.

    Returns:
        Rotation matrices as tensor of shape (n, 3, 3).
    """
    pass


def random_rotation(
        dtype: Optional[torch.dtype] = None, device=None, requires_grad=False
):
    """
    Generate a single random 3x3 rotation matrix.

    Args:
        dtype: Type to return
        device: Device of returned tensor. Default: if None,
            uses the current device for the default tensor type
        requires_grad: Whether the resulting tensor should have the gradient
            flag set

    Returns:
        Rotation matrix as tensor of shape (3, 3).
    """
    pass


def standardize_quaternion(quaternions):
    """
    Convert a unit quaternion to a standard form: one in which the real
    part is non negative.

    Args:
        quaternions: Quaternions with real part first,
            as tensor of shape (..., 4).

    Returns:
        Standardized quaternions as tensor of shape (..., 4).
    """
    pass


def quaternion_raw_multiply(a, b):
    """
    Multiply two quaternions.
    Usual torch rules for broadcasting apply.

    Args:
        a: Quaternions as tensor of shape (..., 4), real part first.
        b: Quaternions as tensor of shape (..., 4), real part first.

    Returns:
        The product of a and b, a tensor of quaternions shape (..., 4).
    """
    pass


def quaternion_multiply(a, b):
    """
    Multiply two quaternions representing rotations, returning the quaternion
    representing their composition, i.e. the versor with nonnegative real part.
    Usual torch rules for broadcasting apply.

    Args:
        a: Quaternions as tensor of shape (..., 4), real part first.
        b: Quaternions as tensor of shape (..., 4), real part first.

    Returns:
        The product of a and b, a tensor of quaternions of shape (..., 4).
    """
    pass


def quaternion_invert(quaternion):
    """
    Given a quaternion representing rotation, get the quaternion representing
    its inverse.

    Args:
        quaternion: Quaternions as tensor of shape (..., 4), with real part
            first, which must be versors (unit quaternions).

    Returns:
        The inverse, a tensor of quaternions of shape (..., 4).
    """
    pass


def quaternion_apply(quaternion, point):
    """
    Apply the rotation given by a quaternion to a 3D point.
    Usual torch rules for broadcasting apply.

    Args:
        quaternion: Tensor of quaternions, real part first, of shape (..., 4).
        point: Tensor of 3D points of shape (..., 3).

    Returns:
        Tensor of rotated points of shape (..., 3).
    """
    pass


def axis_and_d_to_pris_matrix(axis, d):
    """
    Creates a 4x4 matrix that represents a translation along an axis of a distance d
    Works with any number of batch dimensions.

    Args:
        axis: [..., 3]
        d: [ ...]

    Returns: [..., 4, 4]

    """
    pass


def axis_and_angle_to_matrix_44(axis, theta):
    """
    Creates a 4x4 matrix that represents a rotation around an axis by an angle theta.
    Works with any number of batch dimensions.

    Args:
        axis: [..., 3]
        theta: [ ...]

    Returns: [..., 4, 4]

    """
    pass


def axis_and_angle_to_matrix_33(axis, theta):
    """
    Creates a 3x3 matrix that represents a rotation around an axis by an angle theta.
    Works with any number of batch dimensions.

    Argsaxis.sh:
        axis: [..., 3]
        theta: [ ...]

    Returns: [..., 3, 3]

    """
    pass


def axis_angle_to_matrix(axis_angle):
    """
    Convert rotations given as axis/angle to rotation matrices.
    This uses quaternions as an intermediate representation,
    and is a little slower than the other version

    Args:
        axis_angle: Rotations given as a vector in axis angle form,
            as a tensor of shape (..., 3), where the magnitude is
            the angle turned anticlockwise in radians around the
            vector's direction.

    Returns:
        Rotation matrices as tensor of shape (..., 3, 3).
    """
    pass


def matrix_to_axis_angle(matrix):
    """
    Convert rotations given as rotation matrices to axis/angle.

    Args:
        matrix: Rotation matrices as tensor of shape (..., 3, 3).

    Returns:
        Rotations given as a vector in axis angle form, as a tensor
            of shape (..., 3), where the magnitude is the angle
            turned anticlockwise in radians around the vector's
            direction.
    """
    pass


def axis_angle_to_quaternion(axis_angle):
    """
    Convert rotations given as axis/angle to quaternions.

    Args:
        axis_angle: Rotations given as a vector in axis angle form,
            as a tensor of shape (..., 3), where the magnitude is
            the angle turned anticlockwise in radians around the
            vector's direction.

    Returns:
        quaternions with real part first, as tensor of shape (..., 4).
    """
    pass


def quaternion_to_axis_angle(quaternions):
    """
    Convert rotations given as quaternions to axis/angle.

    Args:
        quaternions: quaternions with real part first,
            as tensor of shape (..., 4).

    Returns:
        Rotations given as a vector in axis angle form, as a tensor
            of shape (..., 3), where the magnitude is the angle
            turned anticlockwise in radians around the vector's
            direction.
    """
    pass


def rotation_6d_to_matrix(d6: torch.Tensor) -> torch.Tensor:
    """
    Converts 6D rotation representation by Zhou et al. [1] to rotation matrix
    using Gram--Schmidt orthogonalisation per Section B of [1].
    Args:
        d6: 6D rotation representation, of size (*, 6)

    Returns:
        batch of rotation matrices of size (*, 3, 3)

    [1] Zhou, Y., Barnes, C., Lu, J., Yang, J., & Li, H.
    On the Continuity of Rotation Representations in Neural Networks.
    IEEE Conference on Computer Vision and Pattern Recognition, 2019.
    Retrieved from http://arxiv.org/abs/1812.07035
    """
    pass


def matrix_to_rotation_6d(matrix: torch.Tensor) -> torch.Tensor:
    """
    Converts rotation matrices to 6D rotation representation by Zhou et al. [1]
    by dropping the last row. Note that 6D representation is not unique.
    Args:
        matrix: batch of rotation matrices of size (*, 3, 3)

    Returns:
        6D rotation representation, of size (*, 6)

    [1] Zhou, Y., Barnes, C., Lu, J., Yang, J., & Li, H.
    On the Continuity of Rotation Representations in Neural Networks.
    IEEE Conference on Computer Vision and Pattern Recognition, 2019.
    Retrieved from http://arxiv.org/abs/1812.07035
    """
    pass


def matrix44_to_se3_9d(matrix: torch.Tensor) -> torch.Tensor:
    pass


def se3_9d_to_matrix44(se3: torch.Tensor) -> torch.Tensor:
    pass


def matrix_to_pos_rot(m):
    """Convert 4x4 transformation matrix to (position, xyzw quatnerion) used by pybullet and RViz"""
    pass


def pos_rot_to_matrix(pos, rot):
    pass


# axis sequences for Euler angles
_NEXT_AXIS = [1, 2, 0, 1]

# map axes strings to/from tuples of inner axis, parity, repetition, frame
_AXES2TUPLE = {
    'sxyz': (0, 0, 0, 0),
    'sxyx': (0, 0, 1, 0),
    'sxzy': (0, 1, 0, 0),
    'sxzx': (0, 1, 1, 0),
    'syzx': (1, 0, 0, 0),
    'syzy': (1, 0, 1, 0),
    'syxz': (1, 1, 0, 0),
    'syxy': (1, 1, 1, 0),
    'szxy': (2, 0, 0, 0),
    'szxz': (2, 0, 1, 0),
    'szyx': (2, 1, 0, 0),
    'szyz': (2, 1, 1, 0),
    'rzyx': (0, 0, 0, 1),
    'rxyx': (0, 0, 1, 1),
    'ryzx': (0, 1, 0, 1),
    'rxzx': (0, 1, 1, 1),
    'rxzy': (1, 0, 0, 1),
    'ryzy': (1, 0, 1, 1),
    'rzxy': (1, 1, 0, 1),
    'ryxy': (1, 1, 1, 1),
    'ryxz': (2, 0, 0, 1),
    'rzxz': (2, 0, 1, 1),
    'rxyz': (2, 1, 0, 1),
    'rzyz': (2, 1, 1, 1),
}

_TUPLE2AXES = {v: k for k, v in _AXES2TUPLE.items()}


def quaternion_from_euler(rpy, axes='sxyz'):
    """
    Return quaternion from Euler angles and axis sequence.
    Taken from https://github.com/cgohlke/transformations/blob/master/transformations/transformations.py#L1238

    ai, aj, ak : Euler's roll, pitch and yaw angles
    axes : One of 24 axis sequences as string or encoded tuple

    """
    pass
