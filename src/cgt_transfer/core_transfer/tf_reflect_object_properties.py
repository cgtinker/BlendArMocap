import typing
from typing import Dict
from .. import cgt_tf_object_properties
import bpy


class RuntimeClass:
    """
    Class for copying internal registered properties.
    Pointer Properties to other classes has to be set at generation.
    """
    pass

    def __str__(self):
        s = ["{"]
        for k, v in self.__dict__.items():
            if isinstance(v, RuntimeClass):
                s.append(f"\n\t{k}: ")
                s.append("{")
                for nk, nv in v.__dict__.items():
                    s.append(f"\n\t\t{nk}: {nv},")
                s.append("\n\t},")

            else:
                s.append(f"\n\t{k}: {v},")
        s.append("\n}")
        return "".join(s)

# region DEPRECIATED
# DEPRECIATED - dict to reflect registered property groups in Blender (2.9.3)
cls_type_dict = {
    "OBJECT_PGT_CGT_TransferTarget":     RuntimeClass(),
    "OBJECT_PGT_CGT_RemapDistance":      RuntimeClass(),
    "OBJECT_PGT_CGT_ValueMapping":       RuntimeClass(),
    "OBJECT_PGT_CGT_TransferProperties": RuntimeClass(),
    "Object":                            bpy.types.Object
}


# DEPRECIATED
def copy_ptr_prop_cls(class_name_dict: Dict[str, RuntimeClass]) -> Dict[str, RuntimeClass]:
    """ Uses cls names to copy slots from pointer property groups to flat classes.
        Helper cls improves usage of internal registered types. """
    import warnings
    warnings.warn("DEPRECIATED - Function may only be used in Blender (2.9.0) - (2.9,3)")

    for cls_name in class_name_dict:
        """ Get all registered PropertyGroup properties. """
        cls = getattr(cgt_tf_object_properties, cls_name, None)
        if cls is None:
            continue
        # TODO: static props

        type_hints = typing.get_type_hints(cls)
        id_data = getattr(cls, "id_data", None)
        setattr(class_name_dict[cls_name], 'id_data', id_data)

        for hint in type_hints:
            property_type = type_hints[hint][0].__name__

            # if prop is pointing to sub_cls
            if property_type == 'PointerProperty':
                cls_type_name = type_hints[hint][1]['type'].__name__
                setattr(class_name_dict[cls_name], hint, class_name_dict[cls_type_name])

            else:  # mimic property type
                default_val = type_hints[hint][1].get("default", None)
                enum = type_hints[hint][1].get("items", None)
                if isinstance(enum, typing.Callable):
                    # TODO: static classes for reflection to avoid hacky solution for dynamic enums
                    # dynamic enum -> lf str
                    setattr(class_name_dict[cls_name], hint, "dynamic_enum")

                elif isinstance(enum, typing.Tuple):
                    # tuple of enum elements
                    setattr(class_name_dict[cls_name], hint, enum)

                else:
                    # default val (int / float etc)
                    setattr(class_name_dict[cls_name], hint, type(default_val))
    return class_name_dict
# endregion


def get_runtime_object_attributes(cls_template, obj, cls_out):
    """ Use the runtime dict to get all properties from Object required for remapping. """
    import warnings
    warnings.warn("DEPRECIATED - Function may only be used in Blender (2.9.0) - (2.9,3)")

    for key, value in cls_template.__dict__.items():
        if value == "dynamic_enum":
            if not hasattr(obj, key):
                continue
            # TODO: static classes for reflection to avoid hacky solution for dynamic enums
            # regular a dynamic enum will have a target ob
            if obj.target is not None:
                obj_value = getattr(obj, key, None)
        else:
            obj_value = getattr(obj, key, None)

        if type(value) == RuntimeClass:
            # creating new empty cls and recv
            setattr(cls_out, key, RuntimeClass())
            recv_next_cls = getattr(cls_out, key, RuntimeClass())
            get_object_attributes(value, getattr(obj, key, None), recv_next_cls)
        else:
            setattr(cls_out, key, obj_value)
    return cls_out


def get_object_attributes(cls_template, obj, cls_out):
    """ Use the runtime dict to get all properties from Object required for remapping. """
    for key, value in cls_template.__dict__.get('__annotations__', {}).items():
        obj_value = getattr(obj, key, None)

        if value in (cgt_tf_object_properties.TransferPropertiesProto,
                     cgt_tf_object_properties.ValueMappingProto,
                     cgt_tf_object_properties.RemapDistanceProto,
                     cgt_tf_object_properties.TransferTargetProto):

            # creating new empty cls and recv
            setattr(cls_out, key, RuntimeClass())
            recv_next_cls = getattr(cls_out, key, RuntimeClass())
            get_object_attributes(value, getattr(obj, key, None), recv_next_cls)
        else:
            setattr(cls_out, key, obj_value)
    return cls_out


if __name__ == '__main__':
    ob = bpy.context.selected_objects[0]
    copy_ptr_prop_cls(cls_type_dict)
    res_1 = get_runtime_object_attributes(cgt_tf_object_properties.TransferPropertiesProto, ob.cgt_props, RuntimeClass())
    res_2 = get_runtime_object_attributes(cls_type_dict["OBJECT_PGT_CGT_TransferProperties"], ob.cgt_props, RuntimeClass())
    print("TEMPLATE:", cls_type_dict["OBJECT_PGT_CGT_TransferProperties"], "\n\nCOPY:", res_1)
