# Calculators for Mediapipe data

Calculators specifically for mediapipe landmark list data. 
Every calculator has an update function which takes and returns a `Tuple[data: List[Any], frame: int]`.<br>

The calculators heavily rely on `cgt_utils.cgt_math` and blenders internal `mathutils`.
Many functions used from `mathutils` have and equivalent in `cgt_utils.cgt_math` with lower performance. <br>

The calculators main purpose is to create `Rotation Data` for remapping motions.
Therefore, the input shape and output shape are _not_ consistent. <br>

<b>Input Data</b> <br>
Landmark: `[idx: int, [x: float, y: float, z: float]]`

Pose: `List[Landmarks], Optional[frame: int]`<br>
Face: `List[List[Landmarks]], Optional[frame: int]`<br>
Pose: `List[List[Landmarks], List[Landmarks]], Optional[frame: int]`<br>


<b>Output Data</b> <br>
Location: `[idx: int, List[x: float, y: float, z: float]], Optional[frame: int]`<br>
Rotation: `[idx: int, Euler(x: float, y: float, z: float)], Optional[frame: int]`<br>
Scale: `[idx: int, List[x: float, y: float, z: float]], Optional[frame: int]`<br>

Pose: `List[Location, Rotation, Scale], Optional[frame: int], Optional[frame: int]`<br>
Face: `List[Location, Rotation, Scale], Optional[frame: int], Optional[frame: int]`<br>
Pose: `List[[Location, Location], [Rotation, Rotation], [Scale, Scale]], Optional[frame: int]`<br>
