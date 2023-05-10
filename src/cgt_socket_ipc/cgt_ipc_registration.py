from . import BlendPyNet
import addon_utils  # type: ignore


def register():
    if addon_utils.check('BlendPySock') == (False, False):
        BlendPyNet.register()


def unregister():
    if addon_utils.check('BlendPySock') == (False, False):
        BlendPyNet.unregister()
