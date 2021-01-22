import json

IPYC_CUSTOM_SERIALIZATIONS = {
    dict.__name__: json.dumps,
}

IPYC_CUSTOM_DESERIALIZATIONS = {
    dict.__name__: json.loads,
}


def add_custom_serialization(class_object: object, class_serializer):
    """Register a serialization function for a particular object class. Only
    one serialization method per object is allowed. The method must be a non-
    blocking function.

    .. warning::
        If a custom serializer is defined, ensure a deserializer is defined as well on the receiving end.
        These methods could be ``@classmethod`` methods defined in the class for which you wish to transfer.

    Parameters
    ------------
    class_object: :class:`object`
        The class or object type that will be serialized.
    class_serializer: function
        The function to call when serialization is requested for the object. Must return a string.

    """
    IPYC_CUSTOM_SERIALIZATIONS[class_object.__name__] = class_serializer


def update_custom_serialization(class_object: object, class_serializer):
    """Wrapped method for :meth:`add_custom_serialization`"""
    add_custom_serialization(class_object, class_serializer)


def remove_custom_serialization(class_object: object):
    """De-register a serialization function for a particular object class.

    .. warning::
        If a custom serializer is removed, serialization of this object will then
        default to python's builtins.

    Parameters
    ------------
    class_object: :class:`object`
        The class or object type that will be removed from the custom serializer dictionary.

    """
    if class_object.__name__ in IPYC_CUSTOM_SERIALIZATIONS:
        del IPYC_CUSTOM_SERIALIZATIONS[class_object.__name__]


def add_custom_deserialization(class_object: object, class_deserializer):
    """Register a deserialization function for a particular object class. Only
    one deserialization method per object is allowed. The method must be a non-
    blocking function.

    .. warning::
        If a custom deserializer is defined, ensure a serializer is defined as well on the sending end.
        These methods could be ``@classmethod`` methods defined in the class for which you wish to transfer.

    Parameters
    ------------
    class_object: :class:`object`
        The class or object type that will be serialized.
    class_deserializer: function
        The function to call when deserialization is requested for the object. Must return a :class:`object`.

    """
    IPYC_CUSTOM_DESERIALIZATIONS[class_object.__name__] = class_deserializer


def update_custom_deserialization(class_object: object, class_deserializer):
    """Wrapped method for :meth:`add_custom_deserialization`"""
    add_custom_deserialization(class_object, class_deserializer)


def remove_custom_deserialization(class_object: object):
    """De-register a deserialization function for a particular object class.

    .. warning::
        If a custom deserializer is removed, deserialization of this object will then
        default to python's builtins.

    Parameters
    ------------
    class_object: :class:`object`
        The class or object type that will be removed from the custom deserializer dictionary.

    """
    if class_object.__name__ in IPYC_CUSTOM_DESERIALIZATIONS:
        del IPYC_CUSTOM_DESERIALIZATIONS[class_object.__name__]
