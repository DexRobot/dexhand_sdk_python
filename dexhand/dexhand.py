from ctypes import *
from enum import IntEnum
from pathlib import Path
import platform

myplatform = platform.platform()
mysystem = platform.system()

package_dir = Path(__file__).parent.absolute()

if mysystem == 'Windows':
    dll_dir = (package_dir / '../cpp/sdk/lib/windows').resolve()
    cpplib_path = dll_dir / 'dexhand.dll'
else:
    platform_dir = 'x86_64' if myplatform.__contains__('x86') else 'aarch64'
    cpplib_path = package_dir / '../cpp/sdk/lib/linux/{}/libdexhand.so'.format(platform_dir)

LibDexHand = cdll.LoadLibrary(str(cpplib_path))


class ControlMode(IntEnum):
    """Motor control modes"""
    ZERO_TORQUE = 0x00
    CASCADED_PID = 0x44
    PROTECT_HALL_POSITION = 0x55
    CASCADED_MIT = 0x66


class AdapterType(IntEnum):
    """Supported adapters"""
    if mysystem == 'Windows':
        ZLG_200U = 41
    else:
        ZLG_200U = 33
    ZLG_MINI = 42
    LYS_MINI = 43
    USB2_485 = 485


class DexHand021S:
    def __init__(self, adapter_type=AdapterType.ZLG_200U, adapter_index=0):
        LibDexHand.create_021s.argtypes = [c_ubyte, c_ubyte]
        LibDexHand.create_021s.restype = c_void_p

        LibDexHand.listen_021s.argtypes = [c_void_p, c_bool]

        LibDexHand.set_device_id_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]

        LibDexHand.get_device_id_021s.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_device_id_021s.restype = c_ubyte

        LibDexHand.get_firmware_version_021s.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_firmware_version_021s.restype = c_uint16

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
        LibDexHand.clear_error_021s.argtypes = [c_void_p, c_ubyte]

        LibDexHand.get_error_code_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_error_code_021s.restype = c_ubyte

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

        LibDexHand.get_normal_pressure_delta_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_normal_pressure_delta_021s.restype = c_int

        LibDexHand.get_tangent_pressure_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_tangent_pressure_021s.restype = c_float

        LibDexHand.get_tangent_pressure_delta_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_tangent_pressure_delta_021s.restype = c_int

        LibDexHand.get_tangent_pressure_angle_021s.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_tangent_pressure_angle_021s.restype = c_short

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
        return LibDexHand.get_error_code_021s(self.instance, finger_id, device_id)

    def clear_error(self, device_id):
        LibDexHand.clear_error_021s(self.instance, device_id)

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

    def get_normal_pressure_delta(self, device_id, finger_id):
        return LibDexHand.get_normal_pressure_delta_021s(self.instance, finger_id, device_id)

    def get_tangent_pressure(self, device_id, finger_id):
        return LibDexHand.get_tangent_pressure_021s(self.instance, finger_id, device_id)

    def get_tangent_pressure_delta(self, device_id, finger_id):
        return LibDexHand.get_tangent_pressure_delta_021s(self.instance, finger_id, device_id)

    def get_tangent_pressure_angle(self, device_id, finger_id):
        return LibDexHand.get_tangent_pressure_angle_021s(self.instance, finger_id, device_id)

    def get_approaching_value(self, device_id, finger_id):
        return LibDexHand.get_approaching_value_021s(self.instance, finger_id, device_id)

class ControlLoopArgs(Structure):
    """Whole-frame target of one motor of DexHand-021Lite"""
    _fields_ = [
        ('position', c_int16),
        ('speed', c_uint16),
        ('current', c_uint16),
        ('p1', c_uint16),
        ('p2', c_uint16),
    ]


class MotorState(Structure):
    """Status feedback of one motor of DexHand-021Lite"""
    _fields_ = [
        ('id_current', c_int16),
        ('iq_current', c_int16),
        ('rpm', c_int16),
        ('hall', c_int16),
        ('error_status', c_uint16),
    ]


class DexHand021Lite:
    def __init__(self, serial_port, baud_rate=921600):
        LibDexHand.create_021lite.argtypes = [c_char_p, c_uint32]
        LibDexHand.create_021lite.restype = c_void_p
        LibDexHand.destroy_021lite.argtypes = [c_void_p]

        LibDexHand.disconnect_021lite.argtypes = [c_void_p]

        LibDexHand.set_device_id_021lite.argtypes = [c_void_p, c_ubyte, c_uint16]
        LibDexHand.set_device_id_021lite.restype = c_bool

        LibDexHand.get_device_id_021lite.argtypes = [c_void_p, POINTER(c_ubyte), c_int]
        LibDexHand.get_device_id_021lite.restype = c_ubyte

        LibDexHand.enable_realtime_response_021lite.argtypes = [c_void_p, c_ubyte, c_uint16, c_bool]
        LibDexHand.enable_realtime_response_021lite.restype = c_bool

        LibDexHand.is_alive_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.is_alive_021lite.restype = c_bool

        LibDexHand.get_hand_type_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_hand_type_021lite.restype = c_ubyte

        LibDexHand.get_firmware_version_021lite.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_firmware_version_021lite.restype = c_uint32

        LibDexHand.get_serial_number_021lite.argtypes = [c_void_p, c_ubyte, c_char_p, c_int]
        LibDexHand.get_serial_number_021lite.restype = c_int

        LibDexHand.get_temperature_021lite.argtypes = [c_void_p, c_ubyte, POINTER(c_uint16)]
        LibDexHand.get_temperature_021lite.restype = c_bool

        LibDexHand.enable_021lite.argtypes = [c_void_p, c_ubyte, c_bool]
        LibDexHand.enable_021lite.restype = c_bool

        LibDexHand.move_finger_021lite.argtypes = [c_void_p, c_ubyte, c_ubyte, c_ubyte, c_int16,
                                                   c_uint16, c_uint16, c_uint16, c_uint16, c_int32]

        LibDexHand.move_multiple_fingers_021lite.argtypes = [c_void_p, c_ubyte, c_ubyte,
                                                             POINTER(ControlLoopArgs)]

        LibDexHand.reset_joints_021lite.argtypes = [c_void_p, c_ubyte]

        LibDexHand.home_fingers_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.home_thumb_021lite.argtypes = [c_void_p, c_ubyte]

        LibDexHand.set_safe_temperature_021lite.argtypes = [c_void_p, c_ubyte, c_ubyte, c_uint16]
        LibDexHand.set_safe_temperature_021lite.restype = c_bool

        LibDexHand.get_safe_temperature_021lite.argtypes = [c_void_p, c_ubyte, c_ubyte]
        LibDexHand.get_safe_temperature_021lite.restype = c_uint16

        LibDexHand.clear_error_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.clear_error_021lite.restype = c_bool

        LibDexHand.restore_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.restore_021lite.restype = c_bool

        LibDexHand.set_baud_rate_021lite.argtypes = [c_void_p, c_ubyte, c_ubyte, c_int]
        LibDexHand.set_baud_rate_021lite.restype = c_bool

        LibDexHand.write_user_table_021lite.argtypes = [c_void_p, c_ubyte, POINTER(c_uint16), c_int]
        LibDexHand.write_user_table_021lite.restype = c_bool
        LibDexHand.read_user_table_021lite.argtypes = [c_void_p, c_ubyte, POINTER(c_uint16), c_int]
        LibDexHand.read_user_table_021lite.restype = c_bool
        LibDexHand.read_user_table_values_021lite.argtypes = [c_void_p, c_ubyte, POINTER(c_uint16), c_int]
        LibDexHand.read_user_table_values_021lite.restype = c_bool
        LibDexHand.write_user_table_values_021lite.argtypes = [c_void_p, c_ubyte, POINTER(c_uint16), c_int]
        LibDexHand.write_user_table_values_021lite.restype = c_bool

        LibDexHand.get_hand_status_021lite.argtypes = [c_void_p, c_ubyte, POINTER(MotorState)]
        LibDexHand.get_hand_status_021lite.restype = c_bool

        LibDexHand.get_thumb_degree_021lite.argtypes = [c_void_p, c_ubyte, POINTER(c_int16)]
        LibDexHand.get_thumb_degree_021lite.restype = c_bool

        LibDexHand.get_sys_status_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_sys_status_021lite.restype = c_uint16

        LibDexHand.get_motor_status_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_motor_status_021lite.restype = c_uint16

        LibDexHand.get_enable_status_021lite.argtypes = [c_void_p, c_ubyte]
        LibDexHand.get_enable_status_021lite.restype = c_uint16

        LibDexHand.reboot_021lite.argtypes = [c_void_p, c_ubyte, c_uint16]

        self.instance = LibDexHand.create_021lite(serial_port.encode(), baud_rate)
        if not self.instance:
            raise RuntimeError('Failed to open serial port {}'.format(serial_port))

    def __del__(self):
        instance = getattr(self, 'instance', None)
        if instance:
            LibDexHand.destroy_021lite(instance)
            self.instance = None

    def disconnect(self):
        LibDexHand.disconnect_021lite(self.instance)

    def set_device_id(self, device_id, new_device_id):
        return LibDexHand.set_device_id_021lite(self.instance, device_id, new_device_id)

    def get_device_id(self):
        device_list = (c_ubyte * 1)()
        count = LibDexHand.get_device_id_021lite(self.instance, device_list, 1)
        return device_list[0] if count else None

    def enable_realtime_response(self, device_id, sample_rate, enable=True):
        return LibDexHand.enable_realtime_response_021lite(self.instance, device_id, sample_rate, enable)

    def is_alive(self, device_id):
        return LibDexHand.is_alive_021lite(self.instance, device_id)

    def get_hand_type(self, device_id):
        return LibDexHand.get_hand_type_021lite(self.instance, device_id)

    def get_firmware_version(self, device_id, finger_id):
        return LibDexHand.get_firmware_version_021lite(self.instance, device_id, finger_id)

    def get_serial_number(self, device_id):
        # e.g. DX030-S-L-M-2024BCBBAAAB, 24 chars + '\0'
        buff = create_string_buffer(32)
        LibDexHand.get_serial_number_021lite(self.instance, device_id, buff, len(buff))
        return buff.value.decode(errors='ignore')

    def get_temperature(self, device_id):
        temperature = (c_uint16 * 2)()
        if not LibDexHand.get_temperature_021lite(self.instance, device_id, temperature):
            return None
        return tuple(temperature)

    def enable(self, device_id, enable_all=True):
        return LibDexHand.enable_021lite(self.instance, device_id, enable_all)

    def move_finger(self, device_id, finger_id, mode, position, speed=0, current=0, p1=0, p2=0, delay=10):
        LibDexHand.move_finger_021lite(self.instance, device_id, finger_id, mode,
                                       position, speed, current, p1, p2, delay)

    def move_multiple_fingers(self, device_id, mode, joints):
        targets = [j if isinstance(j, ControlLoopArgs) else ControlLoopArgs(*j) for j in joints]
        LibDexHand.move_multiple_fingers_021lite(self.instance, device_id, mode,
                                                 (ControlLoopArgs * len(targets))(*targets))

    def reset_joints(self, device_id):
        LibDexHand.reset_joints_021lite(self.instance, device_id)

    def home_fingers(self, device_id):
        LibDexHand.home_fingers_021lite(self.instance, device_id)

    def home_thumb(self, device_id):
        LibDexHand.home_thumb_021lite(self.instance, device_id)

    def set_safe_temperature(self, device_id, finger_id, value):
        return LibDexHand.set_safe_temperature_021lite(self.instance, device_id, finger_id, value)

    def get_safe_temperature(self, device_id, finger_id):
        return LibDexHand.get_safe_temperature_021lite(self.instance, device_id, finger_id)

    def clear_error(self, device_id):
        return LibDexHand.clear_error_021lite(self.instance, device_id)

    def restore(self, device_id):
        return LibDexHand.restore_021lite(self.instance, device_id)

    def set_baud_rate(self, device_id, baud_index, adapter_type=AdapterType.USB2_485):
        return LibDexHand.set_baud_rate_021lite(self.instance, device_id, baud_index, adapter_type)

    def write_user_table(self, device_id, reg_addrs):
        reg_addrs = (c_uint16 * len(reg_addrs))(*reg_addrs)
        return LibDexHand.write_user_table_021lite(self.instance, device_id, reg_addrs, len(reg_addrs))

    def read_user_table(self, device_id, count):
        reg_addrs = (c_uint16 * count)()
        if not LibDexHand.read_user_table_021lite(self.instance, device_id, reg_addrs, count):
            return None
        return list(reg_addrs)

    def read_user_table_values(self, device_id, count):
        values = (c_uint16 * count)()
        if not LibDexHand.read_user_table_values_021lite(self.instance, device_id, values, count):
            return None
        return list(values)

    def write_user_table_values(self, device_id, values):
        values = (c_uint16 * len(values))(*values)
        return LibDexHand.write_user_table_values_021lite(self.instance, device_id, values, len(values))

    def get_hand_status(self, device_id):
        status = (MotorState * 6)()
        if not LibDexHand.get_hand_status_021lite(self.instance, device_id, status):
            return None
        return list(status)

    def get_thumb_degree(self, device_id):
        degree = (c_int16 * 2)()
        if not LibDexHand.get_thumb_degree_021lite(self.instance, device_id, degree):
            return None
        return tuple(degree)

    def get_sys_status(self, device_id):
        return LibDexHand.get_sys_status_021lite(self.instance, device_id)

    def get_motor_status(self, device_id):
        return LibDexHand.get_motor_status_021lite(self.instance, device_id)

    def get_enable_status(self, device_id):
        return LibDexHand.get_enable_status_021lite(self.instance, device_id)

    def reboot(self, device_id, mode=0):
        LibDexHand.reboot_021lite(self.instance, device_id, mode)
