import torch

import pytorch_kinematics.transforms as tf
from pytorch_kinematics.transforms import axis_and_angle_to_matrix_33


class Visual(object):
    TYPES = ['box', 'cylinder', 'sphere', 'capsule', 'mesh']

    def __init__(self, offset=None, geom_type=None, geom_param=None):
        pass

    def __repr__(self):
        return "Visual(offset={0}, geom_type='{1}', geom_param={2})".format(self.offset,
                                                                            self.geom_type,
                                                                            self.geom_param)


class Link(object):
    def __init__(self, name=None, offset=None, visuals=()):
        pass

    def to(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "Link(name='{0}', offset={1}, visuals={2})".format(self.name,
                                                                  self.offset,
                                                                  self.visuals)


class Joint(object):
    TYPES = ['fixed', 'revolute', 'prismatic']

    def __init__(self, name=None, offset=None, joint_type='fixed', axis=(0.0, 0.0, 1.0),
                 dtype=torch.float32, device="cpu", limits=None,
                 velocity_limits=None, effort_limits=None):
        pass

    def to(self, *args, **kwargs):
        pass

    def clamp(self, joint_position):
        pass

    def __repr__(self):
        return "Joint(name='{0}', offset={1}, joint_type='{2}', axis={3})".format(self.name,
                                                                                  self.offset,
                                                                                  self.joint_type,
                                                                                  self.axis)


# prefix components:
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '

class Frame(object):
    def __init__(self, name=None, link=None, joint=None, children=None):
        pass

    def __str__(self, prefix='', root=True):
        pointers = [tee] * (len(self.children) - 1) + [last]
        if root:
            ret = prefix + self.name + "\n"
        else:
            ret = ""
        for pointer, child in zip(pointers, self.children):
            ret += prefix + pointer + child.name + "\n"
            if child.children:
                extension = branch if pointer == tee else space
                # i.e. space because last, └── , above so no more |
                ret += child.__str__(prefix=prefix + extension, root=False)
        return ret

    def to(self, *args, **kwargs):
        pass

    def add_child(self, child):
        pass

    def is_end(self):
        pass

    def get_transform(self, theta):
        pass
