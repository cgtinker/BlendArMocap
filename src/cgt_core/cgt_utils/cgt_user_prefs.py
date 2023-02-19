from . import cgt_json
from pathlib import Path
from typing import Any


def get_prefs(**kwargs) -> dict:
    """ Kwargs as key and default value. Ensure to use unique keys (check json if necessary). """
    data = cgt_json.JsonData(PREFERENCES_PATH)
    d = {}
    for key, default in kwargs.items():
        d[key] = getattr(data, key, default)
    return d


def set_prefs(**kwargs) -> None:
    """ Saves new preferences. Ensure to use unique keys (check json if necessary). """
    data = cgt_json.JsonData(PREFERENCES_PATH)
    for key, value in kwargs.items():
        setattr(data, key, value)
    data.save(PREFERENCES_PATH)


def set_nested_attr(cls: Any, attr_path: str, value: Any) -> None:
    """ Set nested property:
        cls[Any]: b.e. bpy.context.scene
        attr_path[str]: b.e. user.properties.name
        -> bpy.context.scene.user.properties.name = value. """
    props = attr_path.split('.')[::-1]
    while len(props) > 0:
        sub_attr = props.pop()
        cls = getattr(cls, sub_attr, None)
    setattr(cls, props[0], value)


# Set path to preference, create file if it doesn't exist.
PREFERENCES_PATH = None
if PREFERENCES_PATH is None:
    PREFERENCES_PATH = Path(__file__).parent / "prefs.json"
    if not PREFERENCES_PATH.is_file():
        with open(PREFERENCES_PATH, 'a') as f:
            f.write('{}')
    PREFERENCES_PATH = str(PREFERENCES_PATH)
