from __future__ import annotations
import logging
import bpy
from typing import Optional


constraints = ['CAMERA_SOLVER', 'FOLLOW_TRACK', 'OBJECT_SOLVER', 'COPY_LOCATION', 'COPY_LOCATION_OFFSET',
               'COPY_LOCATION_WORLD', 'COPY_LOCATION_WORLD_OFFSET', 'COPY_ROTATION', 'COPY_ROTATION_WORLD',
               'COPY_SCALE', 'COPY_TRANSFORMS', 'LIMIT_DISTANCE', 'LIMIT_LOCATION', 'LIMIT_ROTATION', 'LIMIT_SCALE',
               'MAINTAIN_VOLUME', 'TRANSFORM', 'TRANSFORM_CACHE', 'CLAMP_TO', 'DAMPED_TRACK', 'IK', 'LOCKED_TRACK',
               'SPLINE_IK', 'STRETCH_TO', 'TRACK_TO', 'ACTION', 'ARMATURE', 'CHILD_OF', 'FLOOR', 'FOLLOW_PATH', 'PIVOT',
               'SHRINKWRAP']


def check_constraint(obj, **kwargs) -> bool:
    """ Determine if a constraint is already active on an object or
        if it should be added. Takes every kwarg into account. """

    assert 'constraint' in kwargs
    constraint_name = kwargs.pop('constraint')
    assert constraint_name in constraints

    def compare_kwargs(constraint, **kwargs) -> bool:
        # Compare keyword args of the target constraint to the existing constraint.
        # Returns False if any value doesn't match.
        for k, v in kwargs.items():
            try:
                attr_val = getattr(constraint, k)
                if attr_val != v:
                    return False
            except AttributeError:
                logging.warning(f"Attribute Error: {obj} has no attribute {k}: {v}")
        return True

    for obj_constraint in obj.constraints:
        cur_constraint = obj_constraint.name.upper().replace(' ', '_')
        # Check only if constraint types match
        if cur_constraint == constraint_name:
            if compare_kwargs(obj_constraint, **kwargs):
                return True
    return False


def set_constraint(obj, **kwargs) -> Optional[bpy.types.Constraint]:
    """ Adds a constraint to the target object if the object
        doesn't contain a constraint with the same arguments added.
        The constraint props are passed by dicts, sample usage:
            props={"constraint": "COPY_ROTATION", target=bpy.data.objects["Sphere"], use_x=True}
            set_constraint(obj, **props)
    """

    if check_constraint(obj, **kwargs):
        logging.warning(f"Set Constraint Aborted: {obj.name} already has a constraint with matching keyword arguments.")
        return None

    constraint_name = kwargs.pop('constraint')

    def set_kwargs(constraint, **kwargs):
        # set constraint values
        for k, v in kwargs.items():
            try:
                setattr(constraint, k, v)
            except AttributeError:
                logging.warning(f"Attribute Error: {obj} has no attribute {k}: {v}")

    con = obj.constraints.new(constraint_name)
    set_kwargs(con, **kwargs)
    return con
