from typing import Union, Optional, Dict

import mujoco
from mujoco._structs import _MjModelBodyViews as MjModelBodyViews

import pytorch_kinematics.transforms as tf
from . import chain
from . import frame

# Converts from MuJoCo joint types to pytorch_kinematics joint types
JOINT_TYPE_MAP = {
    mujoco.mjtJoint.mjJNT_HINGE: 'revolute',
    mujoco.mjtJoint.mjJNT_SLIDE: "prismatic"
}


def body_to_geoms(m: mujoco.MjModel, body: MjModelBodyViews):
    # Find all geoms which have body as parent
    pass


def _build_chain_recurse(m, parent_frame, parent_body):
    pass


def build_chain_from_mjcf(data, body: Union[None, str, int] = None, assets:Optional[Dict[str,bytes]]=None):
    """
    Build a Chain object from MJCF data.

    Parameters
    ----------
    data : str
        MJCF string data.
    body : str or int, optional
        The name or index of the body to use as the root of the chain. If None, body idx=0 is used.

    Returns
    -------
    chain.Chain
        Chain object created from MJCF.
    """
    pass


def build_serial_chain_from_mjcf(data, end_link_name, root_link_name=""):
    """
    Build a SerialChain object from MJCF data.

    Parameters
    ----------
    data : str
        MJCF string data.
    end_link_name : str
        The name of the link that is the end effector.
    root_link_name : str, optional
        The name of the root link.

    Returns
    -------
    chain.SerialChain
        SerialChain object created from MJCF.
    """
    pass
