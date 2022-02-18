from .driver_interface import Driver


class SinglePropDriver(Driver):
    def prepare(self):
        for idx, var in enumerate(self.variables):
            var.name = self.property_name
            var.type = 'SINGLE_PROP'

            try:
                var.targets[0].id = self.provider_obj
                var.targets[0].data_path = self.data_paths[idx]
            except ReferenceError:
                print(f"Failed to set driver {self.property_name} to {self.target_object.name}")


class BonePropDriver(Driver):
    def prepare(self):
        print("preparing boen prop driver")
        for idx, variable in enumerate(self.variables):
            print(variable)
            variable.name = self.property_name
            variable.type = 'TRANSFORMS'
            variable.targets[0].id = self.target_rig
            variable.targets[0].bone_target = self.provider_obj.name
            trans_path = {
                "location.x": 'LOC_X',
                "location.y": 'LOC_Y',
                "location.z": 'LOC_Z',
                "rotation.x": 'ROT_X',
                "rotation.y": 'ROT_Y',
                "rotation.z": 'ROT_Z',
                "scale.x":    'SCALE_X',
                "scale.y":    'SCALE_Y',
                "scale.z":    'SCALE_Z',
            }
            variable.targets[0].transform_space = 'WORLD_SPACE'
            variable.targets[0].transform_type = trans_path[self.data_paths[idx]]