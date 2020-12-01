import json

IPYC_CUSTOM_SERIALIZATIONS = {
    dict.__name__: json.dumps,
}

IPYC_CUSTOM_DESERIALIZATIONS = {
    dict.__name__: json.loads,
}


def add_custom_serialization(class_object, class_serializer):
    IPYC_CUSTOM_SERIALIZATIONS[class_object.__name__] = class_serializer


def update_custom_serialization(class_object, class_serializer):
    add_custom_serialization(class_object, class_serializer)


def remove_custom_serialization(class_object):
    if class_object.__name__ in IPYC_CUSTOM_SERIALIZATIONS:
        del IPYC_CUSTOM_SERIALIZATIONS[class_object.__name__]


def add_custom_deserialization(class_object, class_deserializer):
    IPYC_CUSTOM_DESERIALIZATIONS[class_object.__name__] = class_deserializer


def update_custom_deserialization(class_object, class_deserializer):
    add_custom_deserialization(class_object, class_deserializer)


def remove_custom_deserialization(class_object):
    if class_object.__name__ in IPYC_CUSTOM_DESERIALIZATIONS:
        del IPYC_CUSTOM_DESERIALIZATIONS[class_object.__name__]
