

def add_driver(target_obj, driver_obj, prop, prop_target,
               dataPath, index=-1, func='', target_rig=None):
    ''' Add driver to obj prop (at index), driven by target data_path '''
    if index != -1:
        driver = target_obj.driver_add(prop, index).driver
    else:
        driver = target_obj.driver_add(prop).driver

    variable = driver.variables.new()
    variable.name = prop_target

    if target_rig is None:
        variable.type = 'SINGLE_PROP'
        try:
            variable.targets[0].id = driver_obj
            variable.targets[0].data_path = dataPath
        except ReferenceError:
            print("missing ik reference object")

    else:
        variable.type = 'TRANSFORMS'
        variable.targets[0].id = target_rig
        variable.targets[0].bone_target = driver_obj.name
        trans_path = {
            "location.x": 'LOC_X',
            "location.y": 'LOC_Y',
            "location.z": 'LOC_Z',
            "rotation.x": 'ROT_X',
            "rotation.y": 'ROT_Y',
            "rotation.z": 'ROT_Z',
            "scale.x": 'SCALE_X',
            "scale.y": 'SCALE_Y',
            "scale.z": 'SCALE_Z',
        }
        variable.targets[0].transform_space = 'WORLD_SPACE'
        variable.targets[0].transform_type = trans_path[dataPath]

    driver.expression = "(" + func + "(" + variable.name + "))" if func else variable.name
