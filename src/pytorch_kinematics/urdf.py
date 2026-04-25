from .urdf_parser_py.urdf import URDF, Mesh, Cylinder, Box, Sphere
from . import frame
from . import chain
import torch
import pytorch_kinematics.transforms as tf

JOINT_TYPE_MAP = {'revolute':   'revolute',
                  'continuous': 'revolute',
                  'prismatic':  'prismatic',
                  'fixed':      'fixed'}


def _convert_transform(origin):
    pass


def _convert_visual(visual):
    pass


def _build_chain_recurse(root_frame, lmap, joints):
    pass


def build_chain_from_urdf(data):
    """
    Build a Chain object from URDF data.

    Parameters
    ----------
    data : str
        URDF string data.

    Returns
    -------
    chain.Chain
        Chain object created from URDF.

    Example
    -------
    >>> import pytorch_kinematics as pk
    >>> data = '''<robot name="test_robot">
    ... <link name="link1" />
    ... <link name="link2" />
    ... <joint name="joint1" type="revolute">
    ...   <parent link="link1"/>
    ...   <child link="link2"/>
    ... </joint>
    ... </robot>'''
    >>> chain = pk.build_chain_from_urdf(data)
    >>> print(chain)
    link1_frame
     	link2_frame

    """
    pass


def build_serial_chain_from_urdf(data, end_link_name, root_link_name=""):
    """
    Build a SerialChain object from urdf data.

    Parameters
    ----------
    data : str
        URDF string data.
    end_link_name : str
        The name of the link that is the end effector.
    root_link_name : str, optional
        The name of the root link.

    Returns
    -------
    chain.SerialChain
        SerialChain object created from URDF.
    """
    pass
