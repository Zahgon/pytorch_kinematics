from .basics import *
import sys
import copy


# @todo Get rid of "import *"
# @todo Make this work with decorators

# Is this reflection or serialization? I think it's serialization...
# Rename?

# Do parent operations after, to allow child to 'override' parameters?
# Need to make sure that duplicate entires do not get into the 'unset*' lists


def reflect(cls, *args, **kwargs):
    """
    Simple wrapper to add XML reflection to an xml_reflection.Object class
    """
    pass


# Rename 'write_xml' to 'write_xml' to have paired 'load/dump', and make
# 'pre_dump' and 'post_load'?
# When dumping to yaml, include tag name?

# How to incorporate line number and all that jazz?
def on_error_stderr(message):
    """ What to do on an error. This can be changed to raise an exception. """
    pass


on_error = on_error_stderr

skip_default = False
# defaultIfMatching = True # Not implemeneted yet

# Registering Types
value_types = {}
value_type_prefix = ''


def start_namespace(namespace):
    """
    Basic mechanism to prevent conflicts for string types for URDF and SDF
    @note Does not handle nesting!
    """
    pass


def end_namespace():
    pass


def add_type(key, value):
    pass


def get_type(cur_type):
    """ Can wrap value types if needed """
    pass


def make_type(cur_type):
    pass


class Path(object):
    def __init__(self, tag, parent=None, suffix="", tree=None):
        self.parent = parent
        self.tag = tag
        self.suffix = suffix
        self.tree = tree  # For validating general path (getting true XML path)

    def __str__(self):
        if self.parent is not None:
            return "{}/{}{}".format(self.parent, self.tag, self.suffix)
        else:
            if self.tag is not None and len(self.tag) > 0:
                return "/{}{}".format(self.tag, self.suffix)
            else:
                return self.suffix


class ParseError(Exception):
    def __init__(self, e, path):
        pass


class ValueType(object):
    """ Primitive value type """

    def from_xml(self, node, path):
        pass

    def write_xml(self, node, value):
        """
        If type has 'write_xml', this function should expect to have it's own
        XML already created i.e., In Axis.to_sdf(self, node), 'node' would be
        the 'axis' element.
        @todo Add function that makes an XML node completely independently?
        """
        pass

    def equals(self, a, b):
        pass


class BasicType(ValueType):
    def __init__(self, cur_type):
        self.type = cur_type

    def to_string(self, value):
        pass

    def from_string(self, value):
        pass


class ListType(ValueType):
    def to_string(self, values):
        pass

    def from_string(self, text):
        pass

    def equals(self, aValues, bValues):
        pass


class VectorType(ListType):
    def __init__(self, count=None):
        self.count = count

    def check(self, values):
        pass

    def to_string(self, values):
        pass

    def from_string(self, text):
        pass


class RawType(ValueType):
    """
    Simple, raw XML value. Need to bugfix putting this back into a document
    """

    def from_xml(self, node, path):
        pass

    def write_xml(self, node, value):
        # @todo rying to insert an element at root level seems to screw up
        # pretty printing
        pass


class SimpleElementType(ValueType):
    """
    Extractor that retrieves data from an element, given a
    specified attribute, casted to value_type.
    """

    def __init__(self, attribute, value_type):
        self.attribute = attribute
        self.value_type = get_type(value_type)

    def from_xml(self, node, path):
        pass

    def write_xml(self, node, value):
        pass


class ObjectType(ValueType):
    def __init__(self, cur_type):
        self.type = cur_type

    def from_xml(self, node, path):
        pass

    def write_xml(self, node, obj):
        pass


class FactoryType(ValueType):
    def __init__(self, name, typeMap):
        pass

    def from_xml(self, node, path):
        pass

    def get_name(self, obj):
        pass

    def write_xml(self, node, obj):
        pass


class DuckTypedFactory(ValueType):
    def __init__(self, name, typeOrder):
        pass

    def from_xml(self, node, path):
        pass

    def write_xml(self, node, obj):
        pass


class Param(object):
    """ Mirroring Gazebo's SDF api

    @param xml_var: Xml name
            @todo If the value_type is an object with a tag defined in it's
                  reflection, allow it to act as the default tag name?
    @param var: Python class variable name. By default it's the same as the
                XML name
    """

    def __init__(self, xml_var, value_type, required=True, default=None,
                 var=None):
        pass

    def set_default(self, obj):
        pass


class Attribute(Param):
    def __init__(self, xml_var, value_type, required=True, default=None,
                 var=None):
        pass

    def set_from_string(self, obj, value):
        """ Node is the parent node in this case """
        pass

    def get_value(self, obj):
        pass

    def add_to_xml(self, obj, node):
        pass


# Add option if this requires a header?
# Like <joints> <joint/> .... </joints> ???
# Not really... This would be a specific list type, not really aggregate


class Element(Param):
    def __init__(self, xml_var, value_type, required=True, default=None,
                 var=None, is_raw=False):
        pass

    def set_from_xml(self, obj, node, path):
        pass

    def add_to_xml(self, obj, parent):
        pass

    def add_scalar_to_xml(self, parent, value):
        pass


class AggregateElement(Element):
    def __init__(self, xml_var, value_type, var=None, is_raw=False):
        pass

    def add_from_xml(self, obj, node, path):
        pass

    def set_default(self, obj):
        pass


class Info:
    """ Small container for keeping track of what's been consumed """

    def __init__(self, node):
        self.attributes = list(node.attrib.keys())
        self.children = xml_children(node)


class Reflection(object):
    def __init__(self, params=[], parent_cls=None, tag=None):
        """ Construct a XML reflection thing
        @param parent_cls: Parent class, to use it's reflection as well.
        @param tag: Only necessary if you intend to use Object.write_xml_doc()
                This does not override the name supplied in the reflection
                definition thing.
        """
        pass

    def set_from_xml(self, obj, node, path, info=None):
        def get_attr_path(attribute):
            pass

        def get_element_path(element):
            pass

        pass

    def add_to_xml(self, obj, node):
        pass


class Object(YamlReflection):
    """ Raw python object for yaml / xml representation """
    XML_REFL = None

    def get_refl_vars(self):
        pass

    def check_valid(self):
        pass

    def pre_write_xml(self):
        """ If anything needs to be converted prior to dumping to xml
        i.e., getting the names of objects and such """
        pass

    def write_xml(self, node):
        """ Adds contents directly to XML node """
        pass

    def to_xml(self):
        """ Creates an overarching tag and adds its contents to the node """
        pass

    def to_xml_string(self, addHeader=True):
        pass

    def post_read_xml(self):
        pass

    def read_xml(self, node, path):
        pass

    @classmethod
    def from_xml(cls, node, path):
        pass

    @classmethod
    def from_xml_string(cls, xml_string):
        pass

    @classmethod
    def from_xml_file(cls, file_path):
        pass

    # Confusing distinction between loading code in object and reflection
    # registry thing...

    def get_aggregate_list(self, xml_var):
        pass

    def aggregate_init(self):
        """ Must be called in constructor! """
        pass

    def add_aggregate(self, xml_var, obj):
        """ NOTE: One must keep careful track of aggregate types for this system.
        Can use 'lump_aggregates()' before writing if you don't care. """
        pass

    def add_aggregates_to_xml(self, node):
        pass

    def remove_aggregate(self, obj):
        pass

    def lump_aggregates(self):
        """ Put all aggregate types together, just because """
        pass

    """ Compatibility """

    def parse(self, xml_string):
        pass


# Really common types
# Better name: element_with_name? Attributed element?
add_type('element_name', SimpleElementType('name', str))
add_type('element_value', SimpleElementType('value', float))

# Add in common vector types so they aren't absorbed into the namespaces
get_type('vector3')
get_type('vector4')
get_type('vector6')
