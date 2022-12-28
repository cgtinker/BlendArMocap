# get transfer props
import typing

from . import cgt_driver_obj_props
import bpy


class RuntimeClass:
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


# reflect registered property groups
cls_type_dict = {
    "OBJECT_PGT_CGT_TransferTarget":     RuntimeClass(),
    "OBJECT_PGT_CGT_RemapDistance":      RuntimeClass(),
    "OBJECT_PGT_CGT_ValueMapping":       RuntimeClass(),
    "OBJECT_PGT_CGT_TransferProperties": RuntimeClass(),
    "Object":                            bpy.types.Object,
}

for cls_name in cls_type_dict:
    """ Get all registered PropertyGroup properties. """
    cls = getattr(cgt_driver_obj_props, cls_name, None)
    if cls is None:
        continue

    type_hints = typing.get_type_hints(cls)
    for hint in type_hints:
        property_type = type_hints[hint][0].__name__

        if property_type == 'PointerProperty':
            cls_type_name = type_hints[hint][1]['type'].__name__
            setattr(cls_type_dict[cls_name], hint, cls_type_dict[cls_type_name])

        else:
            default_val = type_hints[hint][1].get("default", None)
            enum = type_hints[hint][1].get("items", None)
            if isinstance(enum, typing.Callable):
                setattr(cls_type_dict[cls_name], hint, str)
            elif isinstance(enum, typing.Tuple):

                setattr(cls_type_dict[cls_name], hint, enum)
            else:
                setattr(cls_type_dict[cls_name], hint, type(default_val))


def get_attributes(cls_template, obj, cls_out):
    """ Use the runtime dict to get all properties from Object required for remapping. """
    for key, value in cls_template.__dict__.items():
        obj_value = getattr(obj, key, None)

        if type(value) == RuntimeClass:
            setattr(cls_out, key, RuntimeClass())
            recv_next_cls = getattr(cls_out, key, RuntimeClass())
            get_attributes(value, getattr(obj, key, None), recv_next_cls)
        else:
            setattr(cls_out, key, obj_value)
    return cls_out


ob = bpy.context.selected_objects[0]
res = get_attributes(cls_type_dict["OBJECT_PGT_CGT_TransferProperties"], ob.cgt_props, RuntimeClass())
print("TEMPLATE")
print(cls_type_dict["OBJECT_PGT_CGT_TransferProperties"])
print("\nRES")
print(res)
