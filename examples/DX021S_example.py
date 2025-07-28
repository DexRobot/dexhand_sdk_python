import time
from dexhand import *
from dexhand.dexhand import AdapterType


def main():
    hand021s = DexHand021S(adapter_type=AdapterType.ZLG_200U, adapter_index=0)
    hand021s.listen(enable=True)
    device_id = hand021s.get_device_id(channel=0)
    # device_id = 0x01
    # hand021s.set_device_id(device_id)

    print('DexHand-021S is connected, device ID={}'.format(device_id))

    hand021s.enable_realtime_response(device_id=device_id, enable=False)

    hand021s.set_safe_current(device_id=device_id, finger_id=0x01, max_current=250)
    maxCurrent1 = hand021s.get_safe_current(device_id=device_id, finger_id=0x01)
    print('Maximum allowed Current of finger 1 is {}'.format(maxCurrent1))

    hand021s.clear_error(device_id, 0x01)
    hand021s.clear_error(device_id, 0x02)
    hand021s.clear_error(device_id, 0x03)
    hand021s.clear_error(device_id, 0x04)

    hand021s.reset_joints(device_id)
    # time.sleep(1)

    for i in range(5):
        # hand021s.move_finger(device_id, 0x04, 280, 1000, 0x55, 500)
        # time.sleep(1)
        # hand021s.clear_error(device_id, 0x04)

        hand021s.move_finger(device_id, 0x01, 1000, 600, 0x55, 10)
        hand021s.move_finger(device_id, 0x02, 1000, 600, 0x55, 10)
        hand021s.move_finger(device_id, 0x03, 1000, 600, 0x55, 10)

        hand021s.clear_error(device_id, 0x01)
        hand021s.clear_error(device_id, 0x02)
        hand021s.clear_error(device_id, 0x03)

        time.sleep(0.8)

        hand021s.move_finger(device_id, 0x01, 0, 500, 0x55, 10)
        hand021s.move_finger(device_id, 0x02, 0, 500, 0x55, 10)
        hand021s.move_finger(device_id, 0x03, 0, 500, 0x55, 10)

        hand021s.clear_error(device_id, 0x01)
        hand021s.clear_error(device_id, 0x02)
        hand021s.clear_error(device_id, 0x03)
        
        time.sleep(0.8)

        hand021s.reset_joints(device_id)

        current1 = hand021s.get_motor_current(device_id, 0x01)
        print('Current 1={}'.format(current1))

    # error_code1 = hand021s.get_error_code(device_id, 0x01)
    # print('Error of finger 1 = {}'.format(error_code1))


if __name__ == '__main__':
    main()
