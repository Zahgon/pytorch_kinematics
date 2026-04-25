import torch
import math
from .urdf_parser_py.sdf import SDF, Mesh, Cylinder, Box, Sphere
from . import frame
from . import chain
import pytorch_kinematics.transforms as tf

JOINT_TYPE_MAP = {'revolute':  'revolute',
                  'prismatic': 'prismatic',
                  'fixed':     'fixed'}


def _convert_transform(pose):
    pass


def _convert_visuals(visuals):
    pass


def _build_chain_recurse(root_frame, lmap, joints):
    pass


def build_chain_from_sdf(data):
    """
    Build a Chain object from SDF data.

    Parameters
    ----------
    data : str
        SDF string data.

    Returns
    -------
    chain.Chain
        Chain object created from SDF.
    """
    pass


def build_serial_chain_from_sdf(data, end_link_name, root_link_name=""):
    pass
