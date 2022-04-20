def add_bone_property(p_bone, prop_name, value, v_min, v_max, use_soft=False):
    p_bone[prop_name] = value

    if "_RNA_UI" not in p_bone.keys():
        p_bone["_RNA_UI"] = {}

    if use_soft:
        p_bone["_RNA_UI"].update({prop_name: {"use_soft_limits": use_soft, "soft_min": v_min, "soft_max": v_max}})
    else:
        p_bone["_RNA_UI"].update({prop_name: {"min": v_min, "max": v_max}})
