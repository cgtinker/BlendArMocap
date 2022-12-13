import inspect
from src.cgt_core.cgt_bpy import cgt_bpy_utils


class TestCgtBpyUtils(object):
    def test_add_obj(self):
        # add simple obj
        cgt_bpy_utils.add_empty(1, "hello_world")
        assert cgt_bpy_utils.get_object_by_name("hello_world") is None

    def test_add_objs(self):
        # add only if none
        d = {i: f'name_{i}' for i in range(0, 3)}
        cgt_bpy_utils.add_empties(d, 1, '.L')
        for k, v in d.items():
            assert cgt_bpy_utils.get_object_by_name(v + '.L') is not None

        cgt_bpy_utils.set_mode('EDIT')
        # don't add if obj exist
        d = {i: f'name_{i}' for i in range(0, 3)}
        cgt_bpy_utils.add_empties(d, 1, '.L')
        for k, v in d.items():
            assert cgt_bpy_utils.get_object_by_name(v + '.L.001') is None


def main():
    f = TestCgtBpyUtils()
    attrs = (getattr(f, name) for name in dir(f))
    methods = filter(inspect.ismethod, attrs)
    for method in methods:
        try:
            method()
        except TypeError:
            # Can't handle methods with required arguments.
            pass


if __name__ == '__main__':
    main()
