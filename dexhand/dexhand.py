from ctypes import *
from enum import IntEnum
from pathlib import Path

package_dir = Path(__file__).parent.absolute()
cpplib_path = package_dir / '../cpp/sdk/lib/linux' / 'libdexhand.so'
LibDexHand = cdll.LoadLibrary(str(cpplib_path))


class ControlMode(IntEnum):
    """Motor control modes"""
    ZERO_TORQUE = 0x00
    CASCADED_PID = 0x44
    PROTECT_HALL_POSITION = 0x55
    CASCADED_MIT = 0x66


class AdapterType(IntEnum):
    """Supported USB-CANFD adapters"""
    ZLG_200U = 33
    ZLG_MINI = 42
    LYS_MINI = 43


class DexHand021S:
    def __init__(self, adapter_type=AdapterType.ZLG_200U, adapter_index=0):
        LibDexHand.create_021s.argtypes = [c_ubyte, c_ubyte]
        LibDexHand.create_021s.restype = c_void_p

        LibDexHand.listen_021s.argtypes = [c_void_p, c_bool]

        LibDexHand.set_device_id_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]

        LibDexHand.get_device_id_021s.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_device_id_021s.restype = c_ubyte

        LibDexHand.get_firmware_version_021s.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_firmware_version_021s.restype = c_ubyte

        LibDexHand.enable_realtime_response_021s.argtypes = [c_void_p, c_ubyte, c_bool]

        LibDexHand.set_safe_current_021s.argtypes = [c_void_p, c_ubyte, c_ushort, c_ubyte]
        LibDexHand.get_safe_current_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_safe_current_021s.restype = c_ushort

        LibDexHand.set_safe_pressure_021s.argtypes = [c_void_p, c_ubyte, c_ushort, c_ubyte]

        LibDexHand.set_safe_temperature_021s.argtypes = [c_void_p, c_ubyte, c_ubyte, c_ubyte]
        LibDexHand.get_safe_temperature_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_safe_temperature_021s.restype = c_ubyte

        LibDexHand.move_finger_021s.argtypes = [c_void_p, c_ubyte, c_short, c_short, c_ubyte, c_uint, c_ubyte]

        LibDexHand.reset_joints_021s.argtypes = [c_void_p, c_ubyte]
        LibDexHand.clear_error_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]

        LibDexHand.get_motor_current_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_motor_current_021s.restype = c_short

        LibDexHand.get_motor_velocity_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_motor_velocity_021s.restype = c_short

        LibDexHand.get_motor_temperature_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_motor_temperature_021s.restype = c_ubyte

        LibDexHand.get_joint_degree_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_joint_degree_021s.restype = c_float

        LibDexHand.get_normal_pressure_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_normal_pressure_021s.restype = c_float

        LibDexHand.get_tangent_pressure_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_tangent_pressure_021s.restype = c_float

        LibDexHand.get_approaching_value_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_approaching_value_021s.restype = c_int

        self.instance = LibDexHand.create_021s(adapter_type, adapter_index)

    def __del__(self):
        return

    def listen(self, enable):
        LibDexHand.listen_021s(self.instance, enable)

    def set_device_id(self, device_id, channel=0):
        LibDexHand.set_device_id_021s(self.instance, device_id, channel)

    def get_device_id(self, channel=0):
        return LibDexHand.get_device_id_021s(self.instance, channel)

    def get_firmware_version(self, device_id):
        return LibDexHand.get_firmware_version_021s(self.instance, device_id)

    def enable_realtime_response(self, device_id, enable=True):
        LibDexHand.enable_realtime_response_021s(self.instance, device_id, enable)

    def set_safe_current(self, device_id, finger_id, max_current):
        LibDexHand.set_safe_current_021s(self.instance, finger_id, max_current, device_id)

    def get_safe_current(self, device_id, finger_id):
        return LibDexHand.get_safe_current_021s(self.instance, finger_id, device_id)

    def set_safe_pressure(self, device_id, finger_id, max_pressure):
        LibDexHand.set_safe_pressure_021s(self.instance, finger_id, max_pressure, device_id)

    def set_safe_temperature(self, device_id, finger_id, max_temperature):
        LibDexHand.set_safe_temperature_021s(self.instance, finger_id, max_temperature, device_id)

    def get_safe_temperature(self, device_id, finger_id):
        return LibDexHand.get_safe_temperature_021s(self.instance, finger_id, device_id)

    def move_finger(self,
                    device_id,
                    finger_id,
                    target_motion_value,
                    motion_velocity,
                    control_mode=ControlMode.PROTECT_HALL_POSITION,
                    exec_delay=10):
        LibDexHand.move_finger_021s(self.instance, finger_id, target_motion_value, motion_velocity,
                                    control_mode, exec_delay, device_id)

    def reset_joints(self, device_id):
        LibDexHand.reset_joints_021s(self.instance, device_id)

    def get_error_code(self, device_id, finger_id):
        LibDexHand.get_error_code_021s(self.instance, finger_id, device_id)

    def clear_error(self, device_id, finger_id):
        LibDexHand.clear_error_021s(self.instance, finger_id, device_id)

    def get_motor_current(self, device_id, finger_id):
        return LibDexHand.get_motor_current_021s(self.instance, finger_id, device_id)

    def get_motor_velocity(self, device_id, finger_id):
        return LibDexHand.get_motor_velocity_021s(self.instance, finger_id, device_id)

    def get_motor_temperature(self, device_id, finger_id):
        return LibDexHand.get_motor_temperature_021s(self.instance, finger_id, device_id)

    def get_joint_degree(self, device_id, finger_id):
        return LibDexHand.get_joint_degree_021s(self.instance, finger_id, device_id)

    def get_normal_pressure(self, device_id, finger_id):
        return LibDexHand.get_normal_pressure_021s(self.instance, finger_id, device_id)

    def get_tangent_pressure(self, device_id, finger_id):
        return LibDexHand.get_tangent_pressure_021s(self.instance, finger_id, device_id)

    def get_approaching_value(self, device_id, finger_id):
        return LibDexHand.get_approaching_value_021s(self.instance, finger_id, device_id)
