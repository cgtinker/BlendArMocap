Basics
======

Mapping instructions are stored as object properties and can be modified in the `objects constraints` panel.
*Only valid for objects containing a specific cgt_id property.*


Transfer Motion
---------------

The transfer options are location in the ``3D Viewport > BlendAr > Mediapipe``.

Armature
    Select the target armature (b.e. a generated rigify rig for Rigify_Humanoid_DefaultFace_v0.6.1).

Driver Collection
    Select a collection containing driver objects - *cgt_Drivers* to transfer all.
    In some cases you might want to just transfer pose, hands or face results - in this case select a specific collection to do so.

Transfer Type
    Select a transfer configuration.

Load
    Loads the currently selected type to the transfer objects.

Save Config
    Save a new config based on the objects in the *cgt_Drivers* collection.

Transfer Animation
    Load currently selected config for objects in selected collection and transfer the data.
