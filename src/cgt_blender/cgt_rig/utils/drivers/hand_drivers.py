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
                 z_slope: Slope,
                 expansion: list):
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
        self.overwrite = True
        self.data_paths = ["rotation_euler[0]", "rotation_euler[1]", "rotation_euler[2]"]
        self.functions = [
            f"{x_slope.min_out}+{x_slope.slope}*({-x_slope.min_in}+(rotation))",
            # f"(rotation+{expansion[0]})*(rotation+{expansion[1]})",
            # "rotation",
            "",
            ""]
        # f"{z_slope.min_out}+{z_slope.slope}*({-z_slope.min_in}+(rotation))"]


@dataclass(repr=True)
class FingerDriverContainer(DriverContainer):
    # polynomial_expansion = [
    #     [-.5, .15], [-.65, .1], [-.5, .15],  # thumb
    #     [-.5, .15], [-.65, .1], [-.75, 2.0],  # index
    #     [-.5, .15], [-.65, .1], [-1., 0.0],  # middle
    #     [-.5, .15], [-.65, .1], [-.5, .15],  # ring
    #     [-.5, 1.5], [-.65, .1], [-.5, .15],  # pinky
    # ]
    polynomial_expansion = [
        [-.5, .5], [-.65, .1], [-.5, .15],  # thumb
        [-.5, .5], [-.65, .1], [-.75, 2.0],  # index
        [-.5, .5], [-.65, .1], [-1., 0.0],  # middle
        [-.5, .5], [-.65, .1], [-.5, .15],  # ring
        [-.5, 2.], [-.65, .1], [-.5, .15],  # pinky
    ]

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

    # x_inputs = [
    #     [0.004, 0.746], [0.013, 1.015], [0.010, 1.626], # thumb
    #     [0.085, 2.042], [0.011, 2.029], [0.020, 1.513], # index
    #     [0.019, 1.829], [0.017, 1.961], [0.007, 1.937], # middle
    #     [0.010, 2.117], [0.028, 1.888], [0.000, 1.730], # ring
    #     [0.090, 2.162], [0.040, 1.658], [0.012, 2.055] # pinky
    # ]

    x_inputs = [
        [0.01120601124428113, 0.6298811772166859], [0.010113584756535735, 0.5358833537484959],
        [0.0078838400016262, 1.0348199950476649],
        [0.10534613324031182, 1.3311993710360535], [0.014027929045808409, 1.8579332742510741],
        [0.3395665001747216, 1.5229143915770624],
        [0.046080024235105745, 1.3258548962628658], [0.32980177197508853, 1.8030113110176618],
        [0.0070451571969223845, 1.9106269519875598],
        [0.011509957240284703, 1.476811763819492], [0.2437217924936575, 1.6741122935529367],
        [0.021420949714516063, 1.614440408893201],
        [0.11983047278754368, 1.3220586467674347], [0.21275691282569745, 1.583803596524493],
        [0.017777100886813477, 1.9369007101977114]
    ]

    x_outputs = [
        [-.60, 0.6298811772166859], [-.30, 0.5358833537484959], [-.15, 1.0348199950476649],
        [-.50, 1.3311993710360535], [-.20, 1.8579332742510741], [-.55, 1.5229143915770624],
        [-.50, 1.3258548962628658], [-.30, 1.8030113110176618], [-.15, 1.9106269519875598],
        [-.60, 1.4768117638194921], [-.30, 1.6741122935529367], [-.30, 1.614440408893201],
        [-.70, 1.3220586467674347], [-.50, 1.5838035965244931], [-.30, 1.9369007101977114]

    ]
    # x_outputs = [
    #     [-0.830, 0.746], [-0.305, 1.015], [-0.215, 1.626],  # thumb
    #     [-0.590, 2.042], [-0.360, 2.029], [-1.525, 1.513],  # index
    #     [-0.555, 1.829], [-0.790, 1.961], [-0.210, 1.937],  # middle
    #     [-0.540, 2.117], [-0.465, 1.888], [-0.480, 1.730],  # ring
    #     [-0.950, 3.462], [-0.445, 1.668], [-0.455, 2.055]  # pinky
    # ]

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
                self.polynomial_expansion[idx]
            ) for idx, _ in enumerate(driver_targets)]
