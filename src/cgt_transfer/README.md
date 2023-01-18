# Transfer


### Concept
**Object Properties**<br>
Object stores mapping instructions as object properties.
Based on the properties, a driver object gets generated.
The object may also have constraints, which are getting applied to the target to copy values from the driver.

````
mapping_object: object with instructions and constraints
driver_object: generated driver based on instructions
target_object: copies values from driver_object via constraints
````

### Setup Helper
There are some setup helper scripts to generated mapping configs with less effort.
Just copy the raw file into blenders scripting space and modify it.

### Specific Info
**Transfer Management**<br>
Mapping takes place here, at first, gathers information about the passed object properties.
Based on the instructions, drivers objects are getting populated.
Afterwards, constraints based on the input object constrains are getting added to the target object to copy values from the driver.

**Object Properties**<br>
Mapping instructions are getting stored on objects. 
Check the `cgt_tf_object_properties` to get some more information about the properties.
As object properties are stored in the active scene, it's not required to autosave.

**Reflect Properties**<br>
All instruction from the mapping object and also the drivers from the object can be gathered to generate drivers and populate constraints.
Runtime reflection of registered classes sadly support stops at `Blender 3.0+`. Check `cgt_tf_object_properties` and `core_transfer.tf_reflect_object_properties`.

**Driver Generation**<br>
Based on properties, new driver objects are getting generated in `tf_set_object_properties`.
For understanding Driver setup in blender check `cgt_core.cgt_bpy.cgt_drivers`

**Saving and Loading properties**<br>
The object properties and object constraints can be stored in and loaded from .json files, check the `data folder`.
