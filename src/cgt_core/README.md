# Core - Node Chains and Utils...

All registered modules may require the core to run.
When modifying the core, all modules may require testing.<br>
While many core functions are just endpoints, the core introduces a node chain concept.

### Node and Node Chains
On update a node inputs and outputs `data: Any, frame: int`.
The data may change shape during the process. <br>

Benefit of the chain concept:
- composition of nodes instead of inheritance
- get information about every node in the chain or the chain itself by (slightly) modifying `cgt_patterns.cgt_nodes`. 
- can just use a node and ignore the chain

`````
Sample Setup:
InputNode -> CalculatorNode -> OutputNode

Sample Node Chain Group:
mp_holistic_detector 
    -> Face Node Chain
    -> Pose Node Chain
    -> Hand Node Chain
`````

Check `cgt_patterns.cgt_nodes` for more information 
or `cgt_mp_detection_operator` for implementation.

Here a little overview:
- **cgt_bpy** contains tools to modify, access, get and set data within blender
- **cgt_interface** includes base panels which other modules are getting attached to
- **cgt_patterns** contains node pattern
- **cgt_calculator_nodes** to calculate rotations for mediapipe output data
- **cgt_output_nodes** to output processed mediapipe data
- **cgt_utils** features some useful tools (timers, json)