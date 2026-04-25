import string
import yaml
import collections
from lxml import etree


def xml_string(rootXml, addHeader=True):
    # Meh
    pass


def dict_sub(obj, keys):
    pass


def node_add(doc, sub):
    pass


def pfloat(x):
    pass


def xml_children(node):
    children = node.getchildren()

    def predicate(node):
        pass

    return list(filter(predicate, children))


def isstring(obj):
    pass


def to_yaml(obj):
    """ Simplify yaml representation for pretty printing """
    pass


class SelectiveReflection(object):
    def get_refl_vars(self):
        pass


class YamlReflection(SelectiveReflection):
    def to_yaml(self):
        pass

    def __str__(self):
        # Good idea? Will it remove other important things?
        return yaml.dump(self.to_yaml()).rstrip()
