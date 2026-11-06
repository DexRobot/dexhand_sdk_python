import sys
import time
from dexhand import AdapterType, DexHand021Lite, ControlMode


def main():
    default_port = 'COM12' if sys.platform == 'win32' else '/dev/ttyUSB0'
    serial_port = sys.argv[1] if len(sys.argv) > 1 else default_port
    hand = DexHand021Lite(serial_port=serial_port, baud_rate=921600)

    device_id = hand.get_device_id()
    if device_id is None:
        print('No DexHand-021Lite found on {}'.format(serial_port))
        return
    print('DexHand-021Lite is connected, device ID={}'.format(device_id))

    hand.home_fingers(device_id)
    hand.home_thumb(device_id)

    hand.enable_realtime_response(device_id, 10, True)

    print('Hand type={}'.format(hand.get_hand_type(device_id)))
    print('Firmware version={:#x}'.format(hand.get_firmware_version(device_id, 0xFF)))

    temperature = hand.get_temperature(device_id)
    print('Board temperature={}'.format(temperature))

    hand.clear_error(device_id)
    hand.enable(device_id, True)

    # Whole-hand control: all 6 motors in one frame, joint target = (position, speed, current, p1, p2)
    # joint order: 0 index, 1 middle, 2 ring, 3 pinky, 4 thumb bend, 5 thumb rotate

    pose1 = [(1000, 10000, 100, 0, 0)] * 4 + [(0, 10000, 100, 0, 0)] * 2

    pose2 = [(0, 10000, 100, 0, 0)] * 4 + [(3000, 10000, 100, 0, 0)] + [(2000, 10000, 100, 0, 0)]

    for i in range(5):
        hand.move_multiple_fingers(device_id, ControlMode.PROTECT_HALL_POSITION, pose1)
        time.sleep(2)

        hand.move_multiple_fingers(device_id, ControlMode.PROTECT_HALL_POSITION, pose2)
        time.sleep(2)

        status = hand.get_hand_status(device_id)
        if status:

            for motor_id, motor in enumerate(status):
                print('Motor {} status: hall={}, rpm={}, current={}, err={}'.format(
                    motor_id,
                    motor.hall,
                    motor.rpm,
                    motor.id_current,
                    motor.error_status
                ))

    time.sleep(1)

    hand.enable_realtime_response(device_id, 0, False)
    hand.reset_joints(device_id)
    hand.disconnect()


if __name__ == '__main__':
    main()
