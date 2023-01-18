from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

import bpy
from typing import Union


# Get and set custom properties in Blender.
# While it's been tested for Objects and bones it may be used with any property in blender.

def get_custom_property(target_obj: Union[bpy.types.Object, bpy.types.PoseBone], prop_name: str) -> Optional[Any]:
    """ Returns the custom property by name or None. """
    return target_obj.get(prop_name)


def set_custom_property(
        obj: Union[bpy.types.Object, bpy.types.PoseBone], prop_name: str, value: Any,
        v_min: Optional[float] = None, v_max:  Optional[float] = None,
        use_soft: bool = False, overwrite: bool = False) -> bool:

    if get_custom_property(obj, prop_name) is not None and not overwrite:
        return False

    obj[prop_name] = value
    if "_RNA_UI" not in obj.keys():
        obj["_RNA_UI"] = {}

    if use_soft:
        obj["_RNA_UI"].update({prop_name: {"use_soft_limits": use_soft, "soft_min": v_min, "soft_max": v_max}})
    else:
        obj["_RNA_UI"].update({prop_name: {"min": v_min, "max": v_max}})
    return True


@dataclass(repr=True)
class CustomProps:
    """ Custom property data for Blender Objects. """
    name: str
    value: float
    v_min: float
    v_max: float
    use_soft: bool

    def __init__(self, name, value, v_min=None, v_max=None, use_soft=False):
        self.name = name
        self.value = value
        self.v_min = v_min
        self.v_max = v_max
        self.use_soft = use_soft