import bpy


RIGNAME = 'rig'

################################################################
###################### TARGET-BONES ############################
################################################################

# expecting .L / .R suffixes for left and right hand
refs = {
    "thumb_cmc":         "thumb.01",
    "thumb_mcp":         "thumb.02",
    "thumb_ip":          "thumb.03",

    "index_finger_mcp":  "f_index.01",
    "index_finger_pip":  "f_index.02",
    "index_finger_dip":  "f_index.03",

    "middle_finger_mcp": "f_middle.01",
    "middle_finger_pip": "f_middle.02",
    "middle_finger_dip": "f_middle.03",

    "ring_finger_mcp":   "f_ring.01",
    "ring_finger_pip":   "f_ring.02",
    "ring_finger_dip":   "f_ring.03",

    "pinky_mcp":         "f_pinky.01",
    "pinky_pip":         "f_pinky.02",
    "pinky_dip":         "f_pinky.03",

    "wrist":             "hand_ik",
}

##################################################################
####################### MAPPING VALUES ###########################
##################################################################

# x angles overcast when the hand is rotated, limits help to mitigate the issue
constraint_x_limits = [
    [-0.261, 3.14159], [-0.261, 3.1415926], [-0.349, 3.1415926],  # thumb
    [-0.261, 1.22634], [-0.136, 1.3962634], [-0.136, 1.3962634],  # index
    [-0.349, 1.22634], [-0.136, 1.3962634], [-0.136, 1.3962634],  # middle
    [-0.436, 1.22634], [-0.136, 1.3962634], [-0.136, 1.3962634],  # ring
    [-0.698, 1.22634], [-0.136, 1.3962634], [-0.136, 1.3962634],  # pinky
]

# x angles determine the curling and effect mcps, dips and pips
x_inputs = [
    [0.011, 0.630], [0.010, 0.536], [0.008, 1.035],  # thumb
    [0.105, 1.331], [0.014, 1.858], [0.340, 1.523],  # index
    [0.046, 1.326], [0.330, 1.803], [0.007, 1.911],  # middle
    [0.012, 1.477], [0.244, 1.674], [0.021, 1.614],  # ring
    [0.120, 1.322], [0.213, 1.584], [0.018, 1.937],  # pinky
]

x_outputs = [
    [-.60, 0.63], [-.30, 0.54], [-.15, 1.03],  # thumb
    [-.50, 1.33], [-.20, 1.86], [-.55, 1.52],  # index
    [-.50, 1.33], [-.30, 1.80], [-.15, 1.91],  # middle
    [-.60, 1.48], [-.30, 1.67], [-.30, 1.61],  # ring
    [-.80, 1.32], [-.50, 1.58], [-.30, 1.94],  # pinky
]

# z angles determine the spreading range and only effect MCPs
z_inputs = [
    [0.349, 1.047],  # thumb
    [-0.43, 1.047],  # index
    [-0.61, 0.698],  # middle
    [-0.43, 0.698],  # ring
    [-0.69, 0.872],  # pinky
]

z_outputs = [
    [-0.436, 0.4363],  # thumb
    [0.4363, -0.698],  # index
    [0.6108, -0.436],  # middle
    [0.1745, -0.523],  # ring
    [0.3490, -0.523],  # pinky
]


############################################################
###################### TRANSFER ############################
############################################################

def set_hand_properties(rig: bpy.types.Armature, prefix: str = '.L'):
    def set_remap_properties(remap_prop, from_min, from_max, to_min, to_max, factor, offset):
        remap_prop.from_min = from_min
        remap_prop.from_max = from_max
        remap_prop.to_min = to_min
        remap_prop.to_max = to_max
        remap_prop.factor = factor
        remap_prop.offset = offset

    def set_wrist_properties(ob):
        ob.cgt_props.use_rot_x.active = True
        ob.cgt_props.use_rot_y.active = True
        ob.cgt_props.use_rot_z.active = True
        ob.cgt_props.remap_details = 'DEFAULT'

        set_remap_properties(ob.cgt_props.use_rot_x, 0, 1, 0, 1, 1, 0)
        set_remap_properties(ob.cgt_props.use_rot_y, 0, 1, 0, 1, 1, 0)
        set_remap_properties(ob.cgt_props.use_rot_z, 0, 1, 0, 1, 1, 0)

        c = ob.constraints.new(type='COPY_ROTATION')
        c.mix_mode = 'ADD'
        c.owner_space = 'LOCAL'

    for i, entry in enumerate(refs.items()):
        # reference object names
        k, v = entry
        ob_name = 'cgt_' + k + prefix
        bone = v + prefix

        # get ob and clear constraints
        ob = bpy.data.objects.get(ob_name, None)
        assert ob is not None
        ob.constraints.clear()

        # target
        ob.cgt_props.target.obj_type = 'ARMATURE'
        ob.cgt_props.target.target = rig
        ob.cgt_props.target.armature_type = 'BONE'
        ob.cgt_props.target.target_bone = bone

        # driver
        ob.cgt_props.driver_type = 'REMAP'
        ob.cgt_props.by_obj.target_type = 'NONE'

        if k == 'wrist':
            set_wrist_properties(ob)
            continue

        ob.cgt_props.rot_details = True

        # x_vals
        ob.cgt_props.use_rot_x.remap_details = 'DEFAULT'
        x_in_min, x_in_max = x_inputs[i]
        x_out_min, x_out_max = x_outputs[i]
        ob.cgt_props.use_rot_x.active = True
        set_remap_properties(ob.cgt_props.use_rot_x, x_in_min, x_in_max, x_out_min, x_out_max, 1, 0)

        # x limits
        limit_min, limit_max = constraint_x_limits[i]

        c = ob.constraints.new(type='LIMIT_ROTATION')
        c.use_limit_x = True
        c.min_x = limit_min
        c.max_x = limit_max
        c.influence = 1
        c.owner_space = 'LOCAL'

        # z_vals
        if i % 3 == 0:
            z_in_min, z_in_max = z_outputs[i // 3]
            z_out_min, z_out_max = z_outputs[i // 3]
            set_remap_properties(ob.cgt_props.use_rot_x, z_in_min, z_in_max, z_out_min, z_out_max, 1, 0)

            c = ob.constraints.new(type='COPY_ROTATION')
            c.use_y = False
            c.mix_mode = 'ADD'
            c.owner_space = 'LOCAL'

        else:
            c = ob.constraints.new(type='COPY_ROTATION')
            c.use_y = False
            c.use_z = False
            c.mix_mode = 'ADD'
            c.owner_space = 'LOCAL'


def main():
    rig = bpy.data.objects.get(RIGNAME, None)
    if rig is None:
        objs = bpy.context.selected_objects
        assert len(objs) > 0
        assert objs[0].type == 'ARMATURE'
        rig = objs[0]

    assert rig is not None

    set_hand_properties(rig, '.L')
    set_hand_properties(rig, '.R')


if __name__ == '__main__':
    main()
