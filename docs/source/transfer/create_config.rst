Create and customize Configurations
===================================

Setup New Configs
-----------------

The setup process is quite unique, so lets break it down in steps. 
Objects which have been generated during detection contain an ID to display 
additional properties in the *object properties panel*.
Those object properties can be modified to either change the current 
mapping configuration or even create completely new configurations!

The setup options are location in the ``Object constraint properties > BlendArMocap``.

.. note::
    - **mapping object** - an object with instructions and constraints
    - **driver object** - a generated driver object based on instructions
    - **target object** - copies values from driver_object using constraints



Concept
-------

Target
    Target bone or object which should be driven by constraints.
        - Target Type *[Armature, Mesh, Any]*: Apply constraints to target (copies constraints from this object)
        - Sub Target *[Object, Bone]*: Target may be a Bone.

Drivers
    There are three core concepts to set up drivers. 
    In a nutshell *[Remap Drivers, IK Chain Driver, Remap by Distance Drivers]*.


Remap Drivers
    Object values (especially rotations) may get remapped using a remap driver.
    To do so, navigate to *Value Mapping* and select the properties you want to remap - for example *rotation x, y, z*.
    *From min, from max, to min, to max* is used to define slopes, those are similar to the *map range convertor node* in the shader editor.
    Therefore, input the min and max values *in radians* from the selected object and the to min and max values *in radians* you want to have as result. (pi = 180°)
    If necessary, you can also use the *factor* and *offset* however, slopes can deliver better control once you got the hang of them.
    You can do so for all axis separately if necessary, press the *+* icon to do so.
    To get some information about the current select object, navigate to *Tools* and press the *Log Object Info* Button, you'll find min and max values from the object in the info panel.

.. note::
    Remapping object values driver properties

    without remapping object
        slope = (to_max - to_min) / (from_max - from_min)
        offset = to_min - slope * from_min
        f(x) = (slope * property_value + offset) * factor + offset

    with remapping object
        slope = (to_max * remapping_value - to_min * remapping_value) / (from_max - from_min)
        offset = to_min - slope * from_min * remapping_value
        f(x) = (slope * property_value + offset) * factor + offset

IK Chain Drivers
    The idea of ik chain drivers basically is to construct an ik chain in reverse order.
    The end of the ik chain neither has a parent and nor gets remapped - it's mainly a reference.
    The next chain link has the chain end as parent, and gets remapped by the bone length which separates itself from the parent.
    Repeat this till you are at the ik start. As Example:

.. note::
    objects: shoulder_obj -> elbow_obj -> hand_obj
    bones: shoulder_bone -> elbow_bone -> hand_bone

    shoulder_obj(target=shoulder_bone, parent=None, remap_bone=None)
    elbow_obj(target=elbow_bone, parent=shoulder_obj, remap_bone=shoulder_bone.length)
    hand_obj(target=hand_bone, parent=elbow_obj, remap_bone=elbow_bone.length)

    Recursivly applies:
    dist = distance between parent and obj
    f(x) = (dist / remap_bone_length) * (obj_location - previous_chain_obj_location)

Checkout the rigify rig implementation of the arms as example setup.


Remap Drivers by Distance
    When using remap drivers by distance, we aren't using any of the object values.
    In this case, the distance between two objects gets used as driver value, which then gets remapped similar to the remap driver.
    The single difference is that the offset gets multiplied by the remapping value, which allows to basically offset in % (which usually isn't wanted for rotations).
    However, this time it makes a lot of sense to remap the value by a bone of the target armature as we are working with position and not rotation data - this makes remapping the values a lot easier.
    Again, to get some information about the current select object, navigate to *Tools* and press the *Log Object Info* Button, you'll find min and max values from the object in the info panel.

.. note::
    slope = (to_max * remapping_value - to_min * remapping_value) / (from_max - from_min)
    offset = to_min * remapping_value - slope * from_min
    f(x) = (slope * property_value + offset) * factor + offset * remapping_value

Constraints
    Finally, add constraints to the object - the constraints will get applied to the target when transferring.
    As mentioned in the beginning, the target objects copies values from the driver using constraints.
    You may use any constraint to do so and modify the constraint properties to your likings to adjust transfer results.


Tools
-----

Transfer Selection
    Run transfer only for selected objects. When transferring chains the entire chain has to be selected, not just a link.

Smooth Animation Data
    Run Blenders internal smooth f-Curves for selected objects.

Log Object Info
    Log min, max values and information about the selected object to the *info panel*.



I/O Transfer Configuration
--------------------------

Transfer configurations can be imported and exported. 
If you create a new configuration and want to share it with the community let me know via hello@cgtinker.com.

