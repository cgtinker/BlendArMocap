import inspect
from . import cgt_bpy_utils, cgt_constraints
from .cgt_drivers import *


class TestCgtBpyUtils(object):
    def test_add_obj(self):
        # add simple obj
        cgt_bpy_utils.add_empty(1, "hello_world")
        assert (cgt_bpy_utils.get_object_by_name("hello_world").name == "hello_world")

    def test_add_objs(self):
        # add only if none
        d = {i: f'name_{i}' for i in range(0, 3)}
        cgt_bpy_utils.add_empties(d, 1, '.L')
        for k, v in d.items():
            assert cgt_bpy_utils.get_object_by_name(v + '.L').name != None

        # don't add if obj exist
        d = {i: f'name_{i}' for i in range(0, 3)}
        cgt_bpy_utils.add_empties(d, 1, '.L')
        for k, v in d.items():
            assert cgt_bpy_utils.get_object_by_name(v + '.L.001') == None

    def test_custom_properties(self):
        ob = cgt_bpy_utils.get_object_by_name("hello_world")
        value = cgt_object_prop.get_custom_property(ob, "CUSTOM")
        if value == None:
            assigned = cgt_object_prop.set_custom_property(
                obj=ob, prop_name="CUSTOM", value=1337,
                v_min=0, v_max=10000, use_soft=False, overwrite=False
            )
            assert assigned == True
            assert cgt_object_prop.get_custom_property("hello_wold") == 1337

        # testing overwrite
        value = cgt_object_prop.get_custom_property(ob, "CUSTOM")
        if value != None:
            assigned = cgt_object_prop.set_custom_property(
                obj=ob, prop_name="CUSTOM", value=12, overwrite=True
            )
            assert assigned == True

        assert cgt_object_prop.get_custom_property(ob, "CUSTOM") == 12


class TestObjectDrivers(object):
    def test_driver_without_providers(self):
        ob = cgt_bpy_utils.add_empty(1, "target")
        driver = CgtDriver(
            target=ob,
            property_type=CgtPropertyType.loc,
            expressions={0: "sin(frame/25)*5", 1: "cos(frame/25)*5"})
        driver.apply()

    def test_driver_copy_values_from_provider(self):
        ob = cgt_bpy_utils.add_empty(1, "target")
        ob2 = cgt_bpy_utils.add_empty(1, "copy_from_target")
        driver = CgtDriver(
            target=ob2,
            provider_obj=ob,
            property_name="myprop",
            property_type=CgtPropertyType.loc,
            data_paths={i: CgtPropertyType.loc + f'[{i}]' for i in range(0, 3)},
            expressions={0: "myprop/2", 1: "myprop/2"})
        driver.apply()

    def test_driver_copy_multiple(self):
        ob = cgt_bpy_utils.add_empty(1, "target")
        ob2 = cgt_bpy_utils.add_empty(1, "other")
        driver = CgtDriver(
            target=ob2,
            provider_obj=ob,
            property_name="custom_prop",
            property_type=CgtPropertyType.loc,
            data_paths={i: CgtPropertyType.loc + f'[{i}]' for i in range(0, 3)},
            expressions={0: None, 1: None})

        driver.apply()
        driver = CgtDriver(
            target=ob2,
            provider_obj=ob,
            property_name="newTest",
            property_type=CgtPropertyType.loc,
            data_paths={i: CgtPropertyType.loc + f'[{i}]' for i in range(0, 3)},
            expressions={0: "newTest+custom_prop/2", 1: "newTest+custom_prop/2"})
        driver.apply()


class TestBoneDrivers(object):
    def __init__(self):
        if 'Armature' not in bpy.data.objects:
            bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', location=(1.40337, 0, 0), scale=(1, 1, 1))

    def test_simple_bone_driver(self):
        bone = bpy.data.objects['Armature'].pose.bones["Bone"]
        bone.rotation_mode = 'XYZ'
        driver = CgtDriver(
            target=bone,
            property_type=CgtPropertyType.rot,
            expressions={0: "sin(frame/25)*5", 1: "cos(frame/25)", 2: "sin(frame/25)/2"})
        driver.apply()

    def copy_from_bone_driver(self):
        bone = bpy.data.objects['Armature'].pose.bones["Bone"]
        ob2 = cgt_bpy_utils.add_empty(1, "copy_from_bone")
        driver = CgtDriver(
            target=ob2,
            provider_obj=bone,
            property_name="custom_prop",
            property_type=CgtPropertyType.loc,
            data_paths={i: CgtPropertyType.loc + f'[{i}]' for i in range(0, 3)},
            expressions={0: "custom_prop", 1: "custom_prop", 2: "custom_prop"})
        driver.apply()

    def get_single_prop_from_bone(self):
        bone = bpy.data.objects['Armature'].pose.bones["Bone"]
        cube = bpy.data.objects['Cube']
        driver = CgtDriver(
            target=cube,
            property_type=CgtPropertyType.rot,
            expressions={0: "sin(frame/25)*5", 1: "cos(frame/25)", 2: "sin(frame/25)/2"},

            provider_obj=bone,
            property_name="test",
            data_paths={i: f'{CgtPropertyType.loc}[{i}]' for i in range(3)},
            variable_type=CgtVariableType.single_prop,
            transforms_space="WORLD_SPACE")
        driver.apply()

    def get_special_prop_from_bone(self):
        bone = bpy.data.objects['Armature'].pose.bones["Bone"]
        cube = bpy.data.objects['Cube']
        driver = CgtDriver(
            target=cube,
            property_type=CgtPropertyType.loc,
            expressions={0: "len"},

            provider_obj=bone,
            property_name="len",
            data_paths={i: f'length' for i in range(1)},
            variable_type=CgtVariableType.single_prop,
            transforms_space="WORLD_SPACE")

        driver.apply()


class TestConstraints(object):
    def add_constaint(self):
        sp = cgt_bpy_utils.add_empty(1, "sp")
        ob = cgt_bpy_utils.add_empty(1, "ob")
        constraint_props = {
            "constraint": "COPY_ROTATION",
            "target":     sp,
            "use_x":      True
        }

        cgt_constraints.set_constraint(ob, **constraint_props)


def run_class_methods(cls):
    attrs = (getattr(cls, name) for name in dir(cls))
    methods = filter(inspect.ismethod, attrs)
    for method in methods:
        try:
            method()
        except TypeError:
            # Can't handle methods with required arguments.
            pass


def main():
    run_class_methods(TestCgtBpyUtils())
    run_class_methods(TestObjectDrivers())
    run_class_methods(TestBoneDrivers())
    run_class_methods(TestConstraints())


if __name__ == '__main__':
    main()
