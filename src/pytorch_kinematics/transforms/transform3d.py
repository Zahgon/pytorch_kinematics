# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

import math
import typing
import warnings
from typing import Optional

import torch

from .rotation_conversions import _axis_angle_rotation, matrix_to_quaternion, quaternion_to_matrix, \
    euler_angles_to_matrix
from pytorch_kinematics.transforms.perturbation import sample_perturbations
from arm_pytorch_utilities import linalg

DEFAULT_EULER_CONVENTION = "XYZ"


class Transform3d:
    """
    A Transform3d object encapsulates a batch of N 3D transformations, and knows
    how to transform points and normal vectors. Suppose that t is a Transform3d;
    then we can do the following:

    .. code-block:: python

        N = len(t)
        points = torch.randn(N, P, 3)
        normals = torch.randn(N, P, 3)
        points_transformed = t.transform_points(points)    # => (N, P, 3)
        normals_transformed = t.transform_normals(normals)  # => (N, P, 3)


    BROADCASTING
    Transform3d objects supports broadcasting. Suppose that t1 and tN are
    Transform3D objects with len(t1) == 1 and len(tN) == N respectively. Then we
    can broadcast transforms like this:

    .. code-block:: python

        t1.transform_points(torch.randn(P, 3))     # => (P, 3)
        t1.transform_points(torch.randn(1, P, 3))  # => (1, P, 3)
        t1.transform_points(torch.randn(M, P, 3))  # => (M, P, 3)
        tN.transform_points(torch.randn(P, 3))     # => (N, P, 3)
        tN.transform_points(torch.randn(1, P, 3))  # => (N, P, 3)


    COMBINING TRANSFORMS
    Transform3d objects can be combined in two ways: composing and stacking.
    Composing is function composition. Given Transform3d objects t1, t2, t3,
    the following all compute the same thing:

    .. code-block:: python

        y1 = t1.transform_points(t2.transform_points(t3.transform_points(x)))
        y2 = t1.compose(t2).compose(t3).transform_points(x)
        y3 = t1.compose(t2, t3).transform_points(x)


    Composing transforms should broadcast.

    .. code-block:: python

        if len(t1) == 1 and len(t2) == N, then len(t1.compose(t2)) == N.

    We can also stack a sequence of Transform3d objects, which represents
    composition along the batch dimension; then the following should compute the
    same thing.

    .. code-block:: python

        N, M = len(tN), len(tM)
        xN = torch.randn(N, P, 3)
        xM = torch.randn(M, P, 3)
        y1 = torch.cat([tN.transform_points(xN), tM.transform_points(xM)], dim=0)
        y2 = tN.stack(tM).transform_points(torch.cat([xN, xM], dim=0))

    BUILDING TRANSFORMS
    We provide convenience methods for easily building Transform3d objects
    as compositions of basic transforms.

    .. code-block:: python

        # Scale by 0.5, then translate by (1, 2, 3)
        t1 = Transform3d().scale(0.5).translate(1, 2, 3)

        # Scale each axis by a different amount, then translate, then scale
        t2 = Transform3d().scale(1, 3, 3).translate(2, 3, 1).scale(2.0)

        t3 = t1.compose(t2)
        tN = t1.stack(t3, t3)


    BACKPROP THROUGH TRANSFORMS
    When building transforms, we can also parameterize them by Torch tensors;
    in this case we can backprop through the construction and application of
    Transform objects, so they could be learned via gradient descent or
    predicted by a neural network.

    .. code-block:: python

        s1_params = torch.randn(N, requires_grad=True)
        t_params = torch.randn(N, 3, requires_grad=True)
        s2_params = torch.randn(N, 3, requires_grad=True)

        t = Transform3d().scale(s1_params).translate(t_params).scale(s2_params)
        x = torch.randn(N, 3)
        y = t.transform_points(x)
        loss = compute_loss(y)
        loss.backward()

        with torch.no_grad():
            s1_params -= lr * s1_params.grad
            t_params -= lr * t_params.grad
            s2_params -= lr * s2_params.grad

    CONVENTIONS
    We adopt a right-hand coordinate system, meaning that rotation about an axis
    with a positive angle results in a counter clockwise rotation.

    This class assumes that transformations are applied on inputs which
    are column vectors (different from pytorch3d!). The internal representation of the Nx4x4 transformation
    matrix is of the form:

    .. code-block:: python

        M = [
                [Rxx, Ryx, Rzx, Tx],
                [Rxy, Ryy, Rzy, Ty],
                [Rxz, Ryz, Rzz, Tz],
                [0,  0,  0,  1],
            ]

    To apply the transformation to points which are row vectors, the M matrix
    can be pre multiplied by the points:

    .. code-block:: python

        points = [[0, 1, 2]]  # (1 x 3) xyz coordinates of a point
        transformed_point = M @ points[0]
        transformed_points = points @ M.transpose(-1,-2)

    Euler angles given as input by default are interpreted to be in "RXYZ" convention.
    Quaternions given as input should be in [w,x,y,z] order.
    """

    def __init__(
            self,
            default_batch_size=1,
            dtype: torch.dtype = torch.float32,
            device='cpu',
            matrix: Optional[torch.Tensor] = None,
            rot: Optional[typing.Iterable] = None,
            pos: Optional[typing.Iterable] = None,
    ):
        """
        Args:
            default_batch_size: A positive integer representing the minibatch size
                if matrix is None, rot is None, and pos is also None.
            dtype: The data type of the transformation matrix.
                to be used if `matrix = None`.
            device: The device for storing the implemented transformation.
                If `matrix != None`, uses the device of input `matrix`.
            matrix: A tensor of shape (4, 4) or of shape (minibatch, 4, 4)
                representing the 4x4 3D transformation matrix.
                If `None`, initializes with identity using
                the specified `device` and `dtype`.
            rot: A rotation matrix of shape (3, 3) or of shape (minibatch, 3, 3), or
                a quaternion of shape (4,) or of shape (minibatch, 4), where
                minibatch should match that of matrix if that is also passed in.
                The rotation overrides the rotation given in the matrix argument, if any.
                Quaternions must be in wxyz order.
            pos: A tensor of shape (3,) or of shape (minibatch, 3) representing the position
                offsets of the transforms, where minibatch should match that of matrix if
                that is also passed in. The position overrides the position given in the
                matrix argument, if any.
        """
        pass

    def __len__(self):
        return self.get_matrix().shape[0]

    def __getitem__(self, item):
        return Transform3d(matrix=self.get_matrix()[item])

    def __repr__(self):
        m = self.get_matrix()
        pos = m[:, :3, 3]
        rot = matrix_to_quaternion(m[:, :3, :3])
        return "Transform3d(rot={}, pos={})".format(rot, pos).replace('\n       ', '')

    def compose(self, *others):
        """
        Return a new Transform3d with the tranforms to compose stored as
        an internal list.

        Args:
            *others: Any number of Transform3d objects

        Returns:
            A new Transform3d with the stored transforms
        """
        pass

    def get_matrix(self):
        """
        Return the Nx4x4 homogeneous transformation matrix represented by this object.
        """
        pass

    def _get_matrix_inverse(self):
        """
        Return the inverse of self._matrix.
        """
        pass

    @staticmethod
    def _invert_transformation_matrix(T):
        """
        Invert homogeneous transformation matrix.
        """
        pass

    def inverse(self, invert_composed: bool = False):
        """
        Returns a new Transform3D object that represents an inverse of the
        current transformation.

        Args:
            invert_composed: ignored, included for backwards compatibility

        Returns:
            A new Transform3D object containing the inverse of the original
            transformation.
        """
        pass

    def stack(self, *others):
        pass

    def transform_points(self, points, eps: Optional[float] = None, batch_to_batch=False):
        """
        Use this transform to transform a set of 3D points. Assumes row major
        ordering of the input points.

        Args:
            points: Tensor of shape (P, 3) or (N, P, 3)
            eps: If eps!=None, the argument is used to clamp the
                last coordinate before peforming the final division.
                The clamping corresponds to:
                last_coord := (last_coord.sign() + (last_coord==0)) *
                torch.clamp(last_coord.abs(), eps),
                i.e. the last coordinates that are exactly 0 will
                be clamped to +eps.
            batch_to_batch: If True, then each transform is applied to the corresponding point instead of all points.
                Note that this only makes sense if the number of transforms matches the number of points.

        Returns:
            points_out: points of shape (N, P, 3) or (P, 3) depending
            on the dimensions of the transform
        """
        pass

    def transform_normals(self, normals, batch_to_batch=False):
        """
        Use this transform to transform a set of normal vectors.

        Args:
            normals: Tensor of shape (P, 3) or (N, P, 3)
            batch_to_batch: If True, then each transform is applied to the corresponding normal instead of all normals.
                Note that this only makes sense if the number of transforms matches the number of normals.

        Returns:
            normals_out: Tensor of shape (P, 3) or (N, P, 3) depending
            on the dimensions of the transform
        """
        pass

    def transform_shape_operator(self, shape_operators):
        """
        Use this transform to transform a set of shape_operator (or Weingarten map).
        This is the hessian of a signed-distance, i.e. gradient of a normal vector.

        Args:
            shape_operators: Tensor of shape (P, 3, 3) or (N, P, 3, 3)

        Returns:
            shape_operators_out: Tensor of shape (P, 3, 3) or (N, P, 3, 3) depending
            on the dimensions of the transform
        """
        pass

    def translate(self, *args, **kwargs):
        pass

    def scale(self, *args, **kwargs):
        pass

    def rotate(self, *args, **kwargs):
        pass

    def rotate_axis_angle(self, *args, **kwargs):
        pass

    def sample_perturbations(self, num_perturbations, radian_sigma, translation_sigma):
        pass

    def clone(self):
        """
        Deep copy of Transforms object. All internal tensors are cloned
        individually.

        Returns:
            new Transforms object.
        """
        pass

    def to(self, device, copy: bool = False, dtype=None):
        """
        Match functionality of torch.Tensor.to()
        If copy = True or the self Tensor is on a different device, the
        returned tensor is a copy of self with the desired torch.device.
        If copy = False and the self Tensor already has the correct torch.device,
        then self is returned.

        Args:
          device: Device id for the new tensor.
          copy: Boolean indicator whether or not to clone self. Default False.
          dtype: If not None, casts the internal tensor variables
              to a given torch.dtype.

        Returns:
          Transform3d object.
        """
        pass

    def cpu(self):
        pass

    def cuda(self):
        pass


class Translate(Transform3d):
    def __init__(self, x, y=None, z=None, dtype=torch.float32, device: str = "cpu"):
        """
        Create a new Transform3d representing 3D translations.

        Option I: Translate(xyz, dtype=torch.float32, device='cpu')
            xyz should be a tensor of shape (N, 3)

        Option II: Translate(x, y, z, dtype=torch.float32, device='cpu')
            Here x, y, and z will be broadcast against each other and
            concatenated to form the translation. Each can be:
                - A python scalar
                - A torch scalar
                - A 1D torch tensor
        """
        pass

    def _get_matrix_inverse(self):
        """
        Return the inverse of self._matrix.
        """
        pass


class Scale(Transform3d):
    def __init__(self, x, y=None, z=None, dtype=torch.float32, device: str = "cpu"):
        """
        A Transform3d representing a scaling operation, with different scale
        factors along each coordinate axis.

        Option I: Scale(s, dtype=torch.float32, device='cpu')
            s can be one of
                - Python scalar or torch scalar: Single uniform scale
                - 1D torch tensor of shape (N,): A batch of uniform scale
                - 2D torch tensor of shape (N, 3): Scale differently along each axis

        Option II: Scale(x, y, z, dtype=torch.float32, device='cpu')
            Each of x, y, and z can be one of
                - python scalar
                - torch scalar
                - 1D torch tensor
        """
        pass

    def _get_matrix_inverse(self):
        """
        Return the inverse of self._matrix.
        """
        pass


class Rotate(Transform3d):
    def __init__(
            self, R, dtype=torch.float32, device: str = "cpu", orthogonal_tol: float = 1e-5
    ):
        """
        Create a new Transform3d representing 3D rotation using a rotation
        matrix as the input.

        Args:
            R: a tensor of shape (3, 3) or (N, 3, 3)
            orthogonal_tol: tolerance for the test of the orthogonality of R

        """
        pass

    def _get_matrix_inverse(self):
        """
        Return the inverse of self._matrix.
        """
        pass


class RotateAxisAngle(Rotate):
    def __init__(
            self,
            angle,
            axis: str = "X",
            degrees: bool = True,
            dtype=torch.float64,
            device: str = "cpu",
    ):
        """
        Create a new Transform3d representing 3D rotation about an axis
        by an angle.

        Assuming a right-hand coordinate system, positive rotation angles result
        in a counter clockwise rotation.

        Args:
            angle:
                - A torch tensor of shape (N,)
                - A python scalar
                - A torch scalar
            axis:
                string: one of ["X", "Y", "Z"] indicating the axis about which
                to rotate.
                NOTE: All batch elements are rotated about the same axis.
        """
        pass


def _handle_coord(c, dtype, device):
    """
    Helper function for _handle_input.

    Args:
        c: Python scalar, torch scalar, or 1D torch tensor

    Returns:
        c_vec: 1D torch tensor
    """
    pass


def _handle_input(x, y, z, dtype, device, name: str, allow_singleton: bool = False):
    """
    Helper function to handle parsing logic for building transforms. The output
    is always a tensor of shape (N, 3), but there are several types of allowed
    input.

    Case I: Single Matrix
        In this case x is a tensor of shape (N, 3), and y and z are None. Here just
        return x.

    Case II: Vectors and Scalars
        In this case each of x, y, and z can be one of the following
            - Python scalar
            - Torch scalar
            - Torch tensor of shape (N, 1) or (1, 1)
        In this case x, y and z are broadcast to tensors of shape (N, 1)
        and concatenated to a tensor of shape (N, 3)

    Case III: Singleton (only if allow_singleton=True)
        In this case y and z are None, and x can be one of the following:
            - Python scalar
            - Torch scalar
            - Torch tensor of shape (N, 1) or (1, 1)
        Here x will be duplicated 3 times, and we return a tensor of shape (N, 3)

    Returns:
        xyz: Tensor of shape (N, 3)
    """
    pass


def _handle_angle_input(x, dtype, device: str, name: str):
    """
    Helper function for building a rotation function using angles.
    The output is always of shape (N,).

    The input can be one of:
        - Torch tensor of shape (N,)
        - Python scalar
        - Torch scalar
    """
    pass


def _broadcast_bmm(a, b):
    """
    Batch multiply two matrices and broadcast if necessary.

    Args:
        a: torch tensor of shape (P, K) or (M, P, K)
        b: torch tensor of shape (N, K, K)

    Returns:
        a and b broadcast multipled. The output batch dimension is max(N, M).

    To broadcast transforms across a batch dimension if M != N then
    expect that either M = 1 or N = 1. The tensor with batch dimension 1 is
    expanded to have shape N or M.
    """
    pass


def _check_valid_rotation_matrix(R, tol: float = 1e-7):
    """
    Determine if R is a valid rotation matrix by checking it satisfies the
    following conditions:

    ``RR^T = I and det(R) = 1``

    Args:
        R: an (N, 3, 3) matrix

    Returns:
        None

    Emits a warning if R is an invalid rotation matrix.
    """
    pass
