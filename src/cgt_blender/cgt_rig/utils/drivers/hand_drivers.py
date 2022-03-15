from dataclasses import dataclass

from .driver_interface import DriverProperties, DriverContainer, DriverType
from ..mapping import Slope


@dataclass(repr=True)
class FingerAngleDriver(DriverProperties):
    target_object: str
    functions: list

    def __init__(self,
                 driver_target: str,
                 provider_obj: object,
                 x_slope: Slope,
                 z_slope: Slope):
        """ Provides eye driver properties to animate the lids.
            :param provider_obj: object providing rotation values.
            :param slope: factor to multiply and offset the rotation
            :param offset: offsets the base input value
        """

        self.target_object = driver_target
        self.driver_type = DriverType.SINGLE
        self.provider_obj = provider_obj
        self.property_type = "rotation_euler"
        self.property_name = "rotation"
        self.data_paths = ["rotation_euler[0]", "rotation_euler[1]", "rotation_euler[2]"]
        self.functions = [f"{x_slope.min_out}+{x_slope.slope}*({-x_slope.min_in}+(rotation))",
                          "",
                          f"{z_slope.min_out}+{z_slope.slope}*({-z_slope.min_in}+(rotation))"]


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # shifting avgs for L / R hand z-angles
    # thumb / index / middle / ring / pinky
    z_inputs_r = [
        [0.3490658503988659, 1.090830782496456],
        [0.3490658503988659, 1.9198621771937625],
        [0.8726646259971648, 2.007128639793479],
        [1.4835298641951802, 3.141592653589793],
        [1.3089969389957472, 2.8797932657906435]
    ]

    z_inputs_l = [
        [0.3490658503988659, 1.090830782496456],
        [0.5235987755982988, 1.9198621771937625],
        [1.0471975511965976, 2.007128639793479],
        [1.5707963267948966, 2.8797932657906435],
        [1.3089969389957472, 2.792526803190927]
    ]

    z_outputs = [
        [-0.4363323129985824, 0.4363323129985824],
        [0.6108652381980153, -0.3490658503988659],
        [0.5235987755982988, -0.2617993877991494],
        [0.6108652381980153, -0.4363323129985824],
        [0.6108652381980153, -0.4363323129985824]
    ]

    x_inputs = [
        [0.00383972435438, 0.746302788152], [0.01396263401595, 1.015607091735], [0.010297442586766, 1.626472329933],
        [0.08831366015091, 2.042035224833], [0.01151917306316, 2.029817920069], [0.020420352248333, 1.513374994404],
        [0.01937315469713, 1.829105056090], [0.01710422666954, 1.961750079241], [0.007155849933176, 1.937315469713],
        [0.01082104136236, 2.117084382669], [0.02827433388230, 1.888446250657], [0.000872664625997, 1.730668486277],
        [0.09093165402890, 2.162462943220], [0.04014257279586, 1.658760921095], [0.012391837689159, 2.055997858849]]

    x_outputs = [
        [-0.8290313946973066, 0.746302788152], [-0.305432619099, 1.015607091735], [-0.218166156499, 1.626472329933],
        [-1.090830782496456, 2.0420352248333], [-0.567232006898, 2.029817920069], [-1.527163095495, 1.513374994404],
        [-0.6544984694978736, 1.829105056090], [-1.090830782496, 1.961750079241], [-0.218166156499, 1.937315469713],
        [-0.7417649320975901, 2.117084382669], [-0.567232006898, 1.888446250657], [-0.479965544298, 1.730668486277],
        [-1.4398966328953218, 2.162462943220], [-1.047197551196, 1.658760921095], [-0.654498469497, 2.055997858849]]

    def __init__(self, driver_targets: list, provider_objs: list, orientation: str):
        x_slopes = [
            Slope(self.x_inputs[idx][0], self.x_inputs[idx][1], self.x_outputs[idx][0], self.x_outputs[idx][1])
            for idx in range(0, 15)
        ]

        z_slopes_r = [
            Slope(self.z_inputs_r[idx][0], self.z_inputs_r[idx][1], self.z_outputs[idx][0], self.z_outputs[idx][1])
            for idx in range(0, 5)
        ]

        # values have to be mirrored to fit angles
        self.z_outputs = [[i[0] * -1, i[1] * -1] for idx, i in enumerate(self.z_outputs)]
        z_slopes_l = [
            Slope(self.z_inputs_l[idx][0], self.z_inputs_l[idx][1], self.z_outputs[idx][0], self.z_outputs[idx][1])
            for idx in range(0, 5)
        ]

        def get_z_slope(idx):
            if idx not in range(0, 15, 3):
                return Slope(0, 1, 0, 1)

            if orientation == "right":
                return z_slopes_r[int(idx / 3)]
            else:
                return z_slopes_l[int(idx / 3)]

        self.pose_drivers = [
            FingerAngleDriver(
                driver_targets[idx],
                provider_objs[idx],
                x_slopes[idx],
                get_z_slope(idx),
            ) for idx, _ in enumerate(driver_targets)]
