# BlendArMocap is split into separated modules which may access cgt_core.
# Every module has to be registered to be active.

from .cgt_core.cgt_interface import cgt_core_registration
from .cgt_mediapipe import cgt_mp_registration
from .cgt_transfer import cgt_transfer_registration
from .cgt_freemocap import fm_registration


modules = [
    cgt_core_registration,
    cgt_mp_registration,
    fm_registration,
    cgt_transfer_registration,
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()
    