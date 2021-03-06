from abc import ABCMeta
from collections import namedtuple

from six import with_metaclass

from .properties import BaseProperty
from .docs import SharedDocsMeta


__all__ = ('ConfigMeta', 'ConfigABCMeta', 'Configurable', 'ConfigurableABC')


Option = namedtuple('Option', 'class_name value')


class ConfigMeta(SharedDocsMeta):
    """
    Meta-class that configure initialized properties. Also it helps
    inheit properties from parent classes and use them.
    """
    def __new__(cls, clsname, bases, attrs):
        new_class = super(ConfigMeta, cls).__new__(cls, clsname, bases, attrs)
        parents = [kls for kls in bases if isinstance(kls, ConfigMeta)]

        if not hasattr(new_class, 'options'):
            new_class.options = {}

        # Populate parent classes options
        for base_class in parents:
            if hasattr(base_class, 'options'):
                new_class.options = dict(base_class.options,
                                         **new_class.options)

        # Set properties names and save options for different classes
        for key, value in attrs.items():
            if isinstance(value, BaseProperty):
                value.name = key
                new_class.options[key] = Option(class_name=clsname,
                                                value=value)
        return new_class


class BaseConfigurable(object):
    """
    Base configuration class. It help set up and validate
    initialized property values.

    Parameters
    ----------
    **options
        Available properties.
    """
    def __init__(self, **options):
        available_options = set(self.options.keys())
        invalid_options = set(options) - available_options

        if invalid_options:
            print(self.options)
            raise ValueError("Network `{}` contains invalid properties: "
                             "{}".format(self.__class__.__name__,
                                         ', '.join(invalid_options)))

        for key, value in options.items():
            setattr(self, key, value)

        for option_name, option in self.options.items():
            if option.value.required and not getattr(self, option_name):
                raise ValueError("Option `{}` is required."
                                 "".format(option_name))


class Configurable(with_metaclass(ConfigMeta, BaseConfigurable)):
    """
    Class that combine ``BaseConfigurable`` class functionality and
    ``ConfigMeta`` meta-class.
    """


class ConfigABCMeta(ABCMeta, ConfigMeta):
    """
    Meta-class that combains ``ConfigMeta`` and ``abc.ABCMeta``
    meta-classes.
    """


class ConfigurableABC(with_metaclass(ConfigABCMeta, BaseConfigurable)):
    """
    Class that combine ``BaseConfigurable`` class functionality,
    ``ConfigMeta`` and ``abc.ABCMeta`` meta-classes.
    """
