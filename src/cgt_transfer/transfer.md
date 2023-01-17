# Transfer Motion Data


### Concept
Mapping instructions are getting stored as object properties and can be modified in the `objects constraints` panel.
_Once tracking data has been generated you'll find empties in your scene
These Empties contain custom properties (check the constraint properties_

The setup process is quite unique, so lets break it down in steps:
### Target
Target bone or object which should be driven by constraints.
- Target Type `[Armature, Mesh, Any]`: Apply constraints to target which target driver.
- Sub Target `[Object, Bone]`: Target may be a Bone.

### Drivers
There are three core concepts to set up a mapping. In a nutshell `[Remap Drivers, IK Chain Driver, Remap by Distance Drivers]`.<br>


**Remap Drivers**<br>
Object values (especially rotations) may get remapped using a remap driver.
To do so, navigate to `Value Mapping` and select the properties you want to remap - for example `rotation x, y, z`.<br>
`From min, from max, to min, to max` is used to define slopes, similar to the `map range convertor node` in the shader editor.
Therefore, input the min and max values from the selected object and the to min and max values you want to have as result.
If necessary, you can also use the `factor` and `offset` however, slope can deliver better control one you got the hang of them.<br>
You can do so for all axis separately if necessary, press the `+` icon to do so.<br>
To get some information about the current select object, navigate to `Tools` and press the `Log Object Info` Button, you'll find min and max values from the object in the info panel.<br>

``````
# without remapping object
slope = (to_max - to_min) / (from_max - from_min)
offset = to_min - slope * from_min
f(x) = (slope * property_value + offset) * factor + offset

# with remapping object
slope = (to_max * remapping_value - to_min * remapping_value) / (from_max - from_min)
offset = to_min - slope * from_min * remapping_value
f(x) = (slope * property_value + offset) * factor + offset
``````

**IK Chain Drivers**<br>
The idea of ik chain drivers is to construct an ik chain in reverse order.<br>
The end of the ik chain neither has a parent and nor gets remapped.
The next chain link has the chain end as parent, and gets remapped by the bone length separating the targets.
Repeat this till you are at the ik start. As Example:<br>
`````
objects: shoulder_obj -> elbow_obj -> hand_obj
bones: shoulder_bone -> elbow_bone -> hand_bone

shoulder_obj(target=shoulder_bone, parent=None, remap_bone=None)
elbow_obj(target=elbow_bone, parent=shoulder_obj, remap_bone=shoulder_bone.length)
hand_obj(target=hand_bone, parent=elbow_obj, remap_bone=elbow_bone.length)
`````
Checkout the rigify rig implementation of the arms as example setup.<br>


**Remap Drivers by Distance**<br>
When using remap drivers by distance, we aren't using any of the object values.
In this case, a distance between two objects gets used as driver value, which then gets remapped similar to a remap driver.
The single difference is that the offset gets multiplied by the remapping value, which allows to basically offset in % (which usually isn't wanted for rotations).
However, this time it makes a lot of scene to remap the value by a bone of the target armature as we are working with position and not rotation data - this makes remapping the values a lot easier.
Again, to get some information about the current select object, navigate to `Tools` and press the `Log Object Info` Button, you'll find min and max values from the object in the info panel.<br>
``````
slope = (to_max * remapping_value - to_min * remapping_value) / (from_max - from_min)
offset = to_min * remapping_value - slope * from_min
f(x) = (slope * property_value + offset) * factor + offset * remapping_value
``````

