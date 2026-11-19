# DexHand021Lite python SDK 用户文档

## 概览

本文档面向使用 DexHand021Lite Python SDK 进行二次开发的最终用户，覆盖产品的创建、连接、运动控制、状态获取与常用参数设置等全部用户级接口。

DexHand021Lite 通过 485 串口（RTU485 适配器）以 Modbus RTU 协议通讯。CANFD 为后续规划，当前版本暂不支持。跨平台支持 Windows 和 Ubuntu 系统。

Python SDK 基于官方 C\+\+ SDK 的 C 导出接口，通过 `ctypes` 封装为 Python 类 `DexHand021Lite`。库文件随 Python 包一起提供，导入时自动加载，无需手动指定路径。

## 安装与导入

保持`dexhand/`包与`cpp/sdk`库目录的相对位置不变，在项目根目录下即可直接导入。

```Python
from dexhand import (
    DexHand021Lite,        # Lite 灵巧手控制类
    ControlMode,           # 电机控制模式枚举
    ControlLoopArgs,       # 整手控制中的单个关节目标
    MotorState,            # 单电机状态快照
    AdapterType,           # 适配器类型，set_baud_rate 使用
    SystemField,           # 用户自定义表：固定字段码
    MotorParam,            # 用户自定义表：电机参数 offset
    MotorInput,            # 用户自定义表：电机输入 offset
    motor_param_field,     # 拼电机参数字段码
    motor_input_field,     # 拼电机输入字段码
)
```

## 与C\+\+SDK的主要差异

|C\+\+接口|Python实现|
|---|---|
|`createInstance` / `connect(true)`|构造函数 `DexHand021Lite(...)` 内部完成打开串口和启动接收线程|
|`setStatusRxCallback` / `setErrorRxCallback` / `setParamRWCallback`|**未开放**。状态数据通过 `enable_realtime_response()` 开启后台轮询后，用 `get_hand_status()` 读取缓存|
|`errorCode()` / `errorMessage()` / `productType()`|**未开放**，构造失败时抛出 `RuntimeError`|
|`getEnableStatus()`、`clearFirmwareError()`|**未开放**|
|输出参数（如 `uint16_t temperature[2]`）|直接返回 `tuple`，失败返回 `None`|
|写指令类接口返回 `bool`|`move_finger`、`move_multiple_fingers`、`reset_joints`、`reboot` 无返回值|

## 实例创建与销毁

### 1\.1 `DexHand::createInstance`

```Python
DexHand021Lite(serial_port, baud_rate=921600)
```

**功能**：创建一个 DexHand021Lite 实例。构造过程中打开串口并启动数据接收线程，成功后即可直接调用其他接口（等价于 C\+\+ 的 `createInstance` \+ `connect(true)`）。

|参数|类型|说明|
|---|---|---|
|`serial_port`|`str`|485 适配器连接 PC 后分配的串口设备号。Windows 如 `"COM3"`，Linux 如 `"/dev/ttyUSB0"`|
|`baud_rate`|`int`|串口波特率，见附录 A。默认 `921600`|

**异常**：串口打开失败（不存在、被占用等）时抛出`RuntimeError`。

```Python
from dexhand import DexHand021Lite

#根据系统分配的串口号进行填写
hand = DexHand021Lite('COM3')            # 默认 921600
hand = DexHand021Lite('/dev/ttyUSB0', baud_rate=115200)
```

**注意**：

- 用一个串口同时只能被一个实例占用。

- 一条485总线接一只手，实例与设备一一对应。

- 设备波特率与构造参数不一致时无法通讯，需按实际波特率重建实例。

### 1\.2 `disconnect`

```Python
disconnect()
```

**功能**：停止接收线程并关闭串口。调用后设备不再接受本实例的任何指令。无参数、无返回值。

实例被 Python 回收（`del`）时会自动释放内部资源，但建议显式调用 `disconnect()`。

```Python
hand.disconnect()
```

## 运动控制

### 2\.1 `enable`

```Python
enable(device_id, enable_all=True)
```

**功能**：一次性使能/失能整手全部 6 个电机。电机只有在使能状态下才执行运动指令。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备的 Modbus 从机地址|
|`enable_all`|`bool`|`True` 使能全部 6 电机；`False` 全部失能，默认 `True`|

**返回值**：`True` 命令已发送；`False` 发送失败（串口未打开等）。

```Python
hand.enable(device_id, True)
```

**注意**：`device_id` 是整机从机地址，与 DX021 系列的手指板 ID 语义不同。上电后、整帧控制前必须先 `enable(device_id, True)`。

### 2\.2 `move_finger`

```Python
move_finger(device_id, finger_id, mode, position,
speed=0, current=0, p1=0, p2=0, delay=10)
```

**功能**：向指定电机发送一帧运动控制指令。

**注意**：`move_finger` 目前仅支持控制四指；大拇指弯曲和侧摆因固件侧原因不支持使用该方法进行单控，待固件侧优化后可用。控制大拇指请使用 `move_multiple_fingers`（见 2\.3）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备的 Modbus 从机地址|
|`finger_id`|`int`|电机索引 0\~5：0=食指、1=中指、2=无名指、3=小指、4=拇指弯曲、5=拇指侧摆|
|`mode`|`ControlMode` / `int`|控制模式，见下表|
|`position`|`int`|目标位置 AimPos，所有模式均有效（`int16`）|
|`speed`|`int`|AimSpd，模式 0x05/0x06 有效，0x04 忽略，填 0 即可|
|`current`|`int`|0x05 下为 AimCur；0x06 下为前馈力矩 Toffset|
|`p1`|`int`|0x06 下为刚度 Kp；其他模式忽略，填 0 即可|
|`p2`|`int`|0x06 下为阻尼 Kd；其他模式忽略，填 0 即可|
|`delay`|`int`|发送前延时，毫秒，默认 10（`int32`）|

**返回值**：无。

**控制模式**（`ControlMode` 枚举）：

|参数|类型|说明|
|---|---|---|
|`ControlMode.CASCADED_PID`|0x44|position|
|`ControlMode.PROTECT_HALL_POSITION`|0x55|position、speed、current、p1、p2|
|`ControlMode.CASCADED_MIT`|0x66|position、speed、current、p1、p2（MIT 语义）|

**注意**：目前建议只使用 4 和 5 模式,6模式固件侧暂未实现。

**各参数范围**：

||大拇指弯曲|大拇指侧摆|四指弯曲|
|---|---|---|---|
|HallValue|0\-5900|0\-7200|0\-2000|
|速度|2000\-18000|||
|电流|0\-125|||

```Python
#4 模式，食指运动到位置 1000
hand.move_finger(device_id, 0x00, ControlMode.JOINT_POSITION, 1000)

# 5 模式，食指相对运动，速度 10000，电流 100
hand.move_finger(device_id, 0x00, ControlMode.RELATIVE_POSITION, 1000, 10000, 100)
```

### 2\.3 `move_multiple_fingers`

```Python
move_multiple_fingers(device_id, mode, joints)
```

**功能**：整手 6 个关节在一次调用中一起下发运动指令，无需逐个手指调用 2\.2。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备的 Modbus 从机地址|
|`mode`|`ControlMode` / `int`|控制模式，6 个电机共用，取值同 2\.2|
|`joints`|`list`|长度 6 的列表，`joints[i]` 对应电机 i，顺序同 2\.2 的 `finger_id`（0\~3 四指、4 拇指弯曲、5 拇指侧摆）|

`joints` 的每个元素可以是：

- 长度为 5 的元组 `(position, speed, current, p1, p2)`，或

- `ControlLoopArgs` 实例。

**`ControlLoopArgs`** **字段**：

|参数|类型|说明|
|---|---|---|
|`position`|`int16`|目标位置|
|`speed`|`uint16`|目标速度|
|`current`|`uint16`|目标电流|
|`p1`|`uint16`|P1 / Kp|
|`p2`|`uint16`|P2 / Kd|

各字段的实际含义由 `mode` 决定，与 2\.2 的控制模式表一致。

**返回值**：无。

**注意**：需先 `enable(device_id, True)`，否则电机不会响应。整帧接口没有 `delay` 参数，动作节奏请在 Python 侧用 `time.sleep()` 控制。

```Python
#四指不动，大拇指弯曲/侧摆运动
joints = [(0, 0, 0, 0, 0)] * 6
joints[4] = (1500, 15000, 3000, 0, 0)   # 拇指弯曲
joints[5] = (2500, 15000, 3000, 0, 0)   # 拇指侧摆
hand.move_multiple_fingers(device_id, ControlMode.RELATIVE_POSITION, joints)

# 也可以直接传 ControlLoopArgs
joints = [ControlLoopArgs(1000, 0, 0, 0, 0)] * 4 + [ControlLoopArgs(0, 0, 0, 0, 0)] * 2
hand.move_multiple_fingers(device_id, ControlMode.JOINT_POSITION, joints)
```

### 2\.4 `reset_joints`

```Python
reset_joints(device_id)
```

**功能**：将全部 6 个手指关节复位到初始位置。内部对电机进行整帧控制，发送一帧相对位置模式（0x05）运动指令：四指目标位置 0、速度 10000、电流 3000；拇指弯曲/侧摆目标位置 2000、速度 15000、电流 3000。不等待逐帧执行确认。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：无。

**注意**：

- 需先 `enable(device_id, True)`，否则复位指令不会被执行；

- **使用该方法前请确保大拇指与四指的位置不会重叠，防止各关节手指在复位的时候出现“打架”现象，避免设备损坏。**

```Python
hand.reset_joints(device_id)
```

### 2\.5 `home_fingers` / `home_thumb`

```Python
home_fingers(device_id)   # 四指回零
home_thumb(device_id)     # 拇指回零
```

**功能**：上电以后使四指关节或大拇指关节手动回到零位，**设备上电并连接以后，未执行这两条命令时设备拒绝执行运动控制指令**

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：无。

```Python
hand.home_fingers(device_id)
hand.home_thumb(device_id)
```

**注意**：指令送入后立即返回，回零动作由设备执行，不等待完成；建议留出动作时间（`time.sleep()`）后再发送后续运动指令。

## 状态获取

### 3\.1 `enable_realtime_response`

```Python
enable_realtime_response(device_id, sample_rate, enable=True)
```

**功能**：开启/关闭后台轮询线程。开启后每轮读取整手 6 个电机，读完后更新状态缓存；关闭后缓存保留最后一帧数据。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|
|`sample_rate`|`int`|轮询频率。单位 **Hz**（内部间隔 = `1000 / sample_rate` ms）：`50` = 20 ms、`10` = 100 ms。传得越大间隔越小，但实际刷新率受 485 往返时间限制；`0` 在开启轮询时非法（返回 `False`）|
|`enable`|`bool`|`True` 开始轮询；`False` 停止轮询，默认 `True`|

**返回值**：`sample_rate == 0` 且 `enable == True` 时返回 `False`；停止轮询（`enable == False`）总是成功返回 `True`。

```Python
hand.enable_realtime_response(device_id, 10, True)    # 开启轮询
hand.enable_realtime_response(device_id, 10, False)   # 停止轮询
```

**注意**：Python 未开放状态回调，轮询的意义是刷新状态缓存，供 `get_hand_status()` 读取。

### 3\.2 `get_hand_status`

```Python
get_hand_status(device_id)
```

**功能**：读取最近一次轮询的整手电机参数快照（读缓存，不发 Modbus 请求，微秒级返回）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：长度为 6 的 `MotorState` 列表（下标即电机索引 0\~5）；尚未开启轮询、或第一轮轮询尚未完成时返回 `None`。 

**`MotorState`**  **字段**：

|**Python 字段**|**类型**|**含义**|
|---|---|---|
|`id_current`|`int16`|电机电流 Id|
|`iq_current`|`int16`|电机电流 Iq|
|`rpm`|`int16`|电机转速 RPM|
|`hall`|`int16`|Hall 角度基值|
|`error_status`|`uint16`|电机错误位图（定义见附录 B）|

```Python
hand.enable_realtime_response(device_id, 10, True)
time.sleep(0.5)

status = hand.get_hand_status(device_id)
if status is not None:
    for motor_id, motor in enumerate(status):
        print('motor={} id_cur={} iq_cur={} rpm={} hall={} err=0x{:X}'.format(
            motor_id, motor.id_current, motor.iq_current,
            motor.rpm, motor.hall, motor.error_status))
```

**注意**：

- 停止轮询或设备掉线后，继续返回最后一帧旧值，Python 侧暂不提供 `timestamp` 判断新旧；

- 板级温度请用 `get_temperature()`（见 3\.4），拇指角度请用 `get_thumb_degree()`（见 3\.5）；Lite 无力/接近传感器。

### 3\.3 `is_alive`

```Python
is_alive(device_id)
```

**功能**：阻塞式探测指定从机地址的设备是否在线。发送一次设备信息读取，约 100 ms 内收到响应即认为在线。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：`True` 设备应答；`False` 超时无应答（地址错误、设备未上电、串口异常等）。

```Python
if not hand.is_alive(device_id):
    print('Hand not online.')
```

### 3\.4 `get_temperature`

```Python
get_temperature(device_id)
```

**功能**：阻塞式读取设备板级温度（约 100 ms 超时）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：成功返回 `(传感器1, 传感器2)` 元组，均为原始读数（温度×100，如 `2530` 表示 25\.30℃）；失败（超时/无应答/适配器不可用）返回 `None`。

```Python
temp = hand.get_temperature(device_id)
if temp is not None:
    print('Sensor1={:.2f}℃, Sensor2={:.2f}℃'.format(temp[0] / 100, temp[1] / 100))
```

### 3\.5 `get_thumb_degree`

```Python
get_thumb_degree(device_id)
```

**功能**：阻塞式读取拇指两个关节的角度。角度传感器仅拇指（电机 4/5）具备，其余手指无角度数据。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：成功返回 `(拇指弯曲角, 拇指侧摆角)` 元组，对应电机 4、5，单位为“角度值×100”，负值有效；失败返回 `None`。

```Python
degree = hand.get_thumb_degree(device_id)
if degree is not None:
    print('Bend={:.2f} deg, Rotate={:.2f} deg'.format(degree[0] / 100, degree[1] / 100))
```

### 3\.6 `get_sys_status` / `get_motor_status`

```Python
get_sys_status(device_id)     # 各关节在线状态
get_motor_status(device_id)   # 各电机运行/待机状态
```

**功能**：阻塞式读取状态位图（约 100 ms 超时）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：

|**接口**|**位含义**|**读取失败**|
|---|---|---|
|`get_sys_status`|位 N 对应电机 N 的手指板，bit0\~bit5 有效；**1 = 在线、0 = 离线**|`0xFFFF`|
|`get_motor_status`|位 N 对应电机 N，bit0\~bit5 有效；**0 = 运行中、1 = 待机**|`0xFFFF`|

```Python
sys_status = hand.get_sys_status(device_id)
if sys_status != 0xFFFF:          # 先判断是否读取失败
    for i in range(6):
        online = (sys_status & (1 << i)) != 0
```

**注意**：失败返回的 `0xFFFF` 在按 `0x3F` 掩码后会变成 `0x3F`，看起来像“全部在线”，因此必须先与 `0xFFFF` 比较，确认成功后再逐位判断。

### 3\.7 `get_enable_status`

```Python
get_enable_status(device_id)
```

**功能**：阻塞式读取整手 6 个电机的使能状态位图（约 100 ms 超时）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：位 N 对应电机 N，bit0\~bit5 有效（bit6\~bit7 保留）；**1 = 已使能、0 = 未使能**；读取失败返回 `0xFFFF`，判断方式同 3\.6。

```Python
enable_status = hand.get_enable_status(device_id)
if enable_status != 0xFFFF:       # 先判断是否读取失败
    enabled = [(enable_status >> i) & 1 for i in range(6)]
```

## 设备信息查询

### 4\.1 `get_firmware_version`

```Python
get_firmware_version(device_id, finger_id)
```

**功能**：阻塞式读取设备应用固件版本（约 100 ms 超时）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|
|`finger_id`|`int`|`0xFF` = 主控板固件版本；`0~5` = 第 N 个从机板固件版本；其他值返回 0|

**返回值**：成功返回 `(major << 16) | (minor << 8) | patch` 的原始值（`uint32`）；失败返回 0。

```Python
#version = hand.get_firmware_version(device_id, 0xFF)
print('Firmware version={:#x}'.format(version))   # 如 0x10001
#解析为 V1.0.1
print('V{}.{}.{}'.format((version >> 16) & 0x1F, (version >> 8) & 0x1F, version & 0x3F))
```

### 4\.2 `get_hand_type`

```Python
get_hand_type(device_id)
```

**功能**：阻塞式读取手型（左手/右手，约 100 ms 超时）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：

|**返回值**|**含义**|
|---|---|
|`0x00`|左手|
|`0x01`|右手|
|`0x06`|未设置|
|`0xFF`|读取失败|

```Python
hand_type = hand.get_hand_type(device_id)
```

### 4\.3 `get_device_id`

```Python
get_device_id()
```

**功能**：发现总线上灵巧手的从机地址。以广播从机地址 0x00 发起 `SYS_ID` 寄存器读取，设备应答帧中携带其真实从机地址。阻塞到收到应答或超时。

**返回值**：设备的从机地址（`int`）；设备无应答时返回 `None`。

```Python
device_id = hand.get_device_id()
if device_id is None:
    print('No device found on the bus.')
else:
    print('device_id = {}'.format(device_id))
```

**注意**：单设备模型——一条 485 总线只接一只手，接口只返回一个地址；设备出厂默认从机地址为 0x01。

### 4\.4 `get_serial_number`

```Python
get_serial_number(device_id)
```

**功能**：阻塞式读取设备序列号（约 100 ms 超时）。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：成功返回序列号字符串（如 `DX030-S-L-M-2026BCBBAAAB`）；读取失败返回空字符串 `''`。

```Python
sn = hand.get_serial_number(device_id)
if sn:
    print('SN={}'.format(sn))
```

## 参数设置

### 5\.1 `set_safe_temperature` / `get_safe_temperature`

```Python
set_safe_temperature(device_id, finger_id, value)
get_safe_temperature(device_id, finger_id)
```

**功能**：设置/读取单个电机的保护温度。温度达到该值后固件会对过热设备立刻下使能。

**单位说明**：当前版本 set 接口将参数**按原值下发**，因此调用时需自行传入“温度×100”（如 60\.00℃ 传 6000）；get 接口已自动换算，直接返回温度值。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|
|`finger_id`|`int`|电机索引 0\~5，\>=6 时 set 返回 `False`|
|`value`|`int`|写入寄存器的原始值（温度×100）|

**返回值**：

- `set_safe_temperature`：`True` 命令已发送；`False` 参数非法或发送失败；

- `get_safe_temperature`：成功返回换算后的保护温度；失败返回 `0xFF`。

```Python
hand.set_safe_temperature(device_id, 0, 6000)          # 写入 60.00℃
print(hand.get_safe_temperature(device_id, 0))         # 读回约 60
```

### 5\.2 `set_device_id`

```Python
set_device_id(device_id, new_device_id)
```

**功能**：修改设备的从机地址。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备当前从机地址|
|`new_device_id`|`int`|新从机地址（`uint16`）|

**返回值**：`True` 命令已发送；`False` 发送失败。

**注意**：修改成功后设备立即以新地址应答，后续所有调用的 `device_id` 必须换为新地址。

### 5\.3 `set_baud_rate`

```Python
set_baud_rate(device_id, baud_index, adapter_type=AdapterType.USB2_485)
```

**功能**：切换设备 485 总线波特率。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|
|`baud_index`|`int`|波特率索引 0\~5：0=115200、1=230400、2=460800、3=921600、4=1000000、5=2000000；\>5 返回 `False`|
|`adapter_type`|`AdapterType` / `int`|通讯适配器类型。当前仅支持 `AdapterType.USB2_485`（485 适配器），其他类型返回 `False`；默认 `AdapterType.USB2_485`|

**返回值**：`True` 命令已发送；`False` 参数非法、适配器类型不支持或发送失败。

**特别注意**：设备收到指令后即切换到新波特率，**当前实例随即失效**——必须 `disconnect()` 后以新波特率重新构造实例。

```Python
hand.set_baud_rate(device_id, 3)                              # 切到 921600，默认 USB2_485
hand.set_baud_rate(device_id, 5, AdapterType.USB2_485)        # 显式指定适配器类型
hand.disconnect()

hand = DexHand021Lite('/dev/ttyUSB0', baud_rate=921600)
```

### 5\.4 用户自定义表

```Python
write_user_table(device_id, fields)                  # 配置需要的字段（关键字表）
read_user_table_values(device_id, fields)            # 读取字段当前值 -> (bool, list[int])
write_user_table_values(device_id, fields, values)   # 通过表写字段值
```

**功能**：设备侧维护一张"关键字表"，SDK提供所需的字段，这些字段对应的寄存器地址由固件维护，用户只需要使用字段码进行组表配置，之后通过读取表项进行读写。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|
|`fields`|`list[int]`|字段码列表（不可为空）|
|`values`|`list[int]`|字段值列表，与 `fields` 一一对应，长度必须相同|

**返回值**：

|**接口**|**成功**|**失败**|
|---|---|---|
|`write_user_table`|`True`|`False`（空列表或发送失败）|
|`read_user_table_values`|`(True, list[int])`|`(False, [])`|
|`write_user_table_values`|`True`|`False`（空列表、含不可写字段或发送失败）|

**固定字段** **`SystemField`**:

|**名称**|**字段码**|**宽度/含义**|**可写**|
|---|---|---|---|
|`DEVICE_TYPE`|0x00|Uint16|否|
|`MASTER_APP_VERSION`|0x01|Uint16|否|
|`SERIAL_NUMBER_HIGH`|0x02|Uint32 高 16 位|否|
|`SERIAL_NUMBER_LOW`|0x03|Uint32 低 16 位|否|
|`SLAVE0_APP_VERSION`|0x04|Uint16|否|
|`SLAVE1_APP_VERSION`|0x05|Uint16|否|
|`SLAVE2_APP_VERSION`|0x06|Uint16|否|
|`SLAVE3_APP_VERSION`|0x07|Uint16|否|
|`SLAVE4_APP_VERSION`|0x08|Uint16|否|
|`SLAVE5_APP_VERSION`|0x09|Uint16|否|
|`BAUD_RATE`|0x0A|Uint16（0\.\.5）|是|
|`SYS_ID`|0x0B|Uint16|是|
|`APP_LENGTH_HIGH`|0x0C|Uint32 高 16 位|否|
|`APP_LENGTH_LOW`|0x0D|Uint32 低 16 位|否|
|`APP_CHECKSUM_HIGH`|0x0E|Uint32 高 16 位|否|
|`APP_CHECKSUM_LOW`|0x0F|Uint32 低 16 位|否|
|`ANGLE_D4_DEG`|0x10|Int16，角度×100|否|
|`ANGLE_D5_DEG`|0x11|Int16，角度×100|否|
|`ANGLE_D4_RAW`|0x12|Uint16|否|
|`ANGLE_D5_RAW`|0x13|Uint16|否|
|`TEMP1`|0x14|Uint16 原始值|否|
|`TEMP2`|0x15|Uint16 原始值|否|
|`SYS_STATUS`|0x16|Uint16 位图|否|
|`MOTOR_STATUS`|0x17|Uint16 位图|否|

**电机参数 ** **`MotorParam`**（字段码 = `motor_param_field(motor, param)`，motor 0\~5，含义同 `move_finger` 的 `finger_id`）：

|**名称**|**param**|**含义**|**可写**|
|---|---|---|---|
|`POS_KP`|0|位置环 Kp|是|
|`POS_KI`|1|位置环 Ki|是|
|`POS_KD`|2|位置环 Kd|是|
|`POS_MAXOUT`|3|位置环最大输出|是|
|`POS_MINOUT`|4|位置环最小输出|是|
|`POS_MAXIOUT`|5|位置环积分限幅|是|
|`SPD_KP`|6|速度环 Kp|是|
|`SPD_KI`|7|速度环 Ki|是|
|`SPD_KD`|8|速度环 Kd|是|
|`SPD_MAXOUT`|9|速度环最大输出|是|
|`SPD_MINOUT`|10|速度环最小输出|是|
|`SPD_MAXIOUT`|11|速度环积分限幅|是|
|`MOTOR_TYPE`|12|电机类型|否|
|`SAFE_TEMP`|13|保护温度×100|是|

**电机输入 ** **`MotorInput`**（只读，字段码 = `motor_input_field(motor, input)` :

|名称|input|宽度|
|---|---|---|
|`ID_CURRENT`|0|Int16|
|`IQ_CURRENT`|1|Int16|
|`RPM`|2|Int16|
|`HALL`|3|Uint16|
|`HALL_EST`|4|Uint16|
|`ERR_BIT`|5|Uint16（错误位图）|

**字段码 helper**：

```Python
motor_param_field(motor, param)
motor_input_field(motor, input)
```

`motor`、`param`、`input` 越界时抛 `ValueError`。

**数值转换（返回值均为原始 uint16，SDK 不做隐式转换）**：

|字段类型|转换方式|
|---|---|
|Int16（`ID_CURRENT`/`IQ_CURRENT`/`RPM`、`ANGLE_D4_DEG`/`ANGLE_D5_DEG`）|`c_int16(raw).value`（`raw >= 0x8000` 时减 65536）|
|Uint32（`SERIAL_NUMBER_*`、`APP_LENGTH_*`、`APP_CHECKSUM_*`）|`(high << 16) | low`|
|角度 / 温度（`ANGLE_*_DEG`、`SAFE_TEMP`）|`raw / 100.0`|

```Python
import time
from ctypes import c_int16
from dexhand import (SystemField, MotorParam, MotorInput,
                     motor_param_field, motor_input_field)

dev = 1

# 1) 选择字段并配置关键字表
fields = ([motor_param_field(m, MotorParam.POS_KP) for m in range(6)]
          + [motor_input_field(m, MotorInput.IQ_CURRENT) for m in range(6)]
          + [SystemField.DEVICE_TYPE, SystemField.ANGLE_D4_DEG, SystemField.ANGLE_D5_DEG])

print('writeUserTable:', 'queued' if hand.write_user_table(dev, fields) else 'failed')
time.sleep(0.1)

# 2) 读镜像值，values[i] 对应 fields[i]
ok, values = hand.read_user_table_values(dev, fields)
if not ok:
    print('readUserTableValues failed')
else:
    pos_kp = values[0:6]
    iq = [c_int16(v).value for v in values[6:12]]
    device_type, angle4, angle5 = values[12:15]
    print('DEVICE_TYPE=0x{:X}'.format(device_type))
    print('ANGLE_D4_DEG={}  ANGLE_D5_DEG={}  (0.01 deg)'.format(
        c_int16(angle4).value, c_int16(angle5).value))

# 3) 写可写字段：SAFE_TEMP = 65.00℃
hand.write_user_table_values(dev, [motor_param_field(0, MotorParam.SAFE_TEMP)], [6500])
```

**注意**：

1. `write_user_table` 只配置字段，不发送数值；

2. `read_user_table_values` 请求的字段应在设备当前关键字表内；读失败返回 `(False, [])`

3. `write_user_table_values` 只接受可写保持寄存器字段；出现只读字段或电机输入字段时，整次返回 `False`，且一条都不发送。

4. `fields` 与 `values` 长度不一致时抛 `ValueError`；`fields` 中的值不在 0\~0xFFFF 时抛 `OverflowError` / `TypeError`。

5. 数量上限由 C 侧判断（保持寄存器组 80 个、输入寄存器组 176 个），超限返回 `False`。

## 错误处理与维护

### 6\.1 `clear_error`

```Python
clear_error(device_id)
```

**功能**：清除设备的堵转状态（错误位图见附录 B）。排除物理故障后调用，设备恢复正常执行能力。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：`True` 命令已发送；`False` 发送失败。

### 6\.2 `reboot`

```Python
reboot(device_id, mode=0)
```

**功能**：重启设备。发送后设备重启，重启期间不响应指令，需等待设备重新上线后再通讯。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|
|`mode`|`int`|`0` = 整链复位（默认）；`1` = 仅复位从机|

**返回值**：无。命令为单向发送，不等待设备应答。

```Python
hand.reboot(device_id)        # 整链复位
hand.reboot(device_id, 1)     # 仅复位从机
```

### 6\.3 `restore`

```Python
restore(device_id)
```

**功能**：恢复设备出厂设置，所有持久化参数恢复为出厂值。

|参数|类型|说明|
|---|---|---|
|`device_id`|`int`|设备从机地址|

**返回值**：`True` 命令已发送；`False` 发送失败。

**注意**：恢复出厂后地址/波特率可能改变，当前实例可能需要按出厂参数重建，调用前请确认设备出厂默认值。

## 完整示例

```Python
import time
from dexhand import DexHand021Lite, ControlMode

# 1. 创建实例（内部自动打开串口并启动接收线程）
serial_port = 'COM3'          # Ubuntu 下如 '/dev/ttyUSB0'
hand = DexHand021Lite(serial_port, baud_rate=921600)

# 2. 通过广播获取设备从机地址
device_id = hand.get_device_id()
if device_id is None:
    print('Device not available.')
    raise SystemExit(-1)

# 3. 探测在线并读取设备信息
if not hand.is_alive(device_id):
    print('Hand not online.')
    hand.disconnect()
    raise SystemExit(-1)

master = hand.get_firmware_version(device_id, 0xFF)   # 主控板
slave0 = hand.get_firmware_version(device_id, 0x00)   # 从机板 0
print('master V{}.{}.{}, slave0 V{}.{}.{}'.format(
    (master >> 16) & 0x1F, (master >> 8) & 0x1F, master & 0x3F,
    (slave0 >> 16) & 0x1F, (slave0 >> 8) & 0x1F, slave0 & 0x3F))
print('Hand type={:#x}'.format(hand.get_hand_type(device_id)))
print('SN={}'.format(hand.get_serial_number(device_id)))

# 4. 回零（上电后必须完成，否则手拒绝执行运动指令）
hand.home_fingers(device_id)
hand.home_thumb(device_id)
time.sleep(0.5)

# 5. 使能并运动
hand.clear_error(device_id)
hand.enable(device_id, True)
hand.move_finger(device_id, 0x00, ControlMode.PROTECT_HALL_POSITION, 1000, 10000, 100)

# 6. 开启实时轮询并读取缓存
hand.enable_realtime_response(device_id, 50, True)
time.sleep(0.5)

status = hand.get_hand_status(device_id)
if status is not None:
    for motor_id, motor in enumerate(status):
        print('motor={} id_cur={} iq_cur={} rpm={} hall={} err=0x{:X}'.format(
            motor_id, motor.id_current, motor.iq_current,
            motor.rpm, motor.hall, motor.error_status))

# 7. 复位/失能并断开
hand.enable_realtime_response(device_id, 50, False)
hand.reset_joints(device_id)
time.sleep(0.5)
hand.enable(device_id, False)
hand.disconnect()
```

## 使用注意事项

1. 构造函数即完成打开串口和连接，失败时抛出 `RuntimeError`，应及时捕获处理。

2. **上电后必须先调用 ** **`home_fingers()`** **和  ** **`home_thumb()`** **完成回零**，否则手会拒绝执行电机控制指令。

3. 整手控制和复位前必须先 `enable(device_id, True)`，否则电机不会响应。

4. `set_baud_rate` 成功后必须以新波特率重建实例；`restore` 后需确认设备出厂默认地址/波特率。

5. 写类接口返回 `True` 仅代表命令发送成功，设备执行结果需通过状态轮询确认。

6. `device_id` 为 Modbus 从机地址（整机地址），与 DX021 的手指板 ID 语义不同，不可混用。

7. Python 未开放 C\+\+ 的状态/错误/参数回调，状态数据只能通过 `enable_realtime_response()` \+ `get_hand_status()` 轮询获取。

8. 阻塞式接口（`is_alive`、`get_firmware_version`、`get_temperature`、`get_thumb_degree`、`get_sys_status`、`get_motor_status`、`get_enable_status`、`get_serial_number`、`get_device_id` 等）单次超时约 100 ms，在多设备/高频指令场景下注意请求节奏，避免命令交叠。

9. `move_multiple_fingers`整帧接口没有 `delay` 参数，节奏用 `time.sleep()` 控制。

10. 用户自定义表的 `fields` 不能为空；字段码必须是合法字段，数量上限由 C 侧判断（保持寄存器组 80 个、输入寄存器组 176 个）；`write_user_table_values` 只接受可写字段。

11. CANFD 传输尚未为 021Lite 提供，后续版本补充。

## 附录

### 附录 A：`BaudRate` 可选值

Windows 为本地枚举，Linux 为 `LibSerial::BaudRate` 别名，数值一致：

|**波特率**|**对应 ** **`baud_index`**|
|---|---|
|115200|0|
|230400|1|
|460800|2|
|921600（构造默认值）|3|
|1000000|4|
|2000000|5|

### 附录 B：电机错误位 `MotorErrorCode_021Lite`

|位|值|含义|
|---|---|---|
|bit0|0x0001|温度|
|bit1|0x0002|过流|
|bit2|0x0004|过压|
|bit3|0x0008|堵转|
|bit4|0x0010|缺相|
|bit5|0x0020|角度|
|bit6|0x0040|霍尔偏置错误|
|bit7|0x0080|欠压|
|bit8|0x0100|短路|
|bit9|0x0200|失步|
|bit10|0x0400|编码器错误|
|bit11|0x0800|电流采样错误|

### 附录 C：Modbus 异常码 `R485LiteErrorCode`

|值|含义|
|---|---|
|0x01|功能码错误|
|0x02|非法地址|
|0x03|非法数据|
|0x04|从机故障|
|0x05|处理缓慢|
|0x06|从机忙|
|0x07|无响应|
|0x0B|不允许|

### 附录 D：Python 与 C\+\+ 接口对照

|**功能**|**C\+\+ 接口**|**Python 接口**|
|---|---|---|
|创建实例|`createInstance` / 构造 \+ `connect(true)`|`DexHand021Lite(serial_port, baud_rate)`|
|断开|`disconnect()`|`disconnect()`|
|使能|`enable(deviceId, enableAll)`|`enable(device_id, enable_all)`|
|单指控制|`moveFinger(...)`|`move_finger(...)`|
|整手控制|`moveMultipleFingers(deviceId, desc)`|`move_multiple_fingers(device_id, mode, joints)`|
|关节复位|`resetJoints(deviceId)`|`reset_joints(device_id)`|
|四指回零|`homeFingers(deviceId)`|`home_fingers(device_id)`|
|拇指回零|`homeThumb(deviceId)`|`home_thumb(device_id)`|
|开启轮询|`setRealtimeResponse(deviceId, sampleRate, enable)`|`enable_realtime_response(device_id, sample_rate, enable)`|
|读取状态|`getHandStatus(deviceId)`|`get_hand_status(device_id)`|
|在线探测|`isAlive(channel, deviceId)`|`is_alive(device_id)`|
|板级温度|`getTemperature(deviceId, uint16_t[2])`|`get_temperature(device_id)`|
|拇指角度|`getThumbDegree(deviceId, int16_t[2])`|`get_thumb_degree(device_id)`|
|关节在线|`getSysStatus(deviceId)`|`get_sys_status(device_id)`|
|电机运行状态|`getMotorStatus(deviceId)`|`get_motor_status(device_id)`|
|固件版本|`getFirmwareVersion(deviceId, fingerId)`|`get_firmware_version(device_id, finger_id)`|
|手型|`getHandType(deviceId)`|`get_hand_type(device_id)`|
|从机地址发现|`getSysIds(channel, list)`|`get_device_id()`|
|序列号|`getSerialNumber(deviceId)`|`get_serial_number(device_id)`|
|保护温度|`setSafeTemperature` / `getSafeTemperature`|`set_safe_temperature` / `get_safe_temperature`|
|修改从机地址|`setSysId(deviceId, newSysId)`|`set_device_id(device_id, new_device_id)`|
|修改波特率|`setBaudRate(deviceId, baudIndex, adapterType)`|`set_baud_rate(device_id, baud_index, adapter_type)`|
|用户表配置字段|`writeUserTable(deviceId, table)`|`write_user_table(device_id, fields)`|
|用户表读值|`readUserTableValues(deviceId, table)`|`read_user_table_values(device_id, fields)`|
|用户表写值|`writeUserTableValues(deviceId, table)`|`write_user_table_values(device_id, fields, values)`|
|清错误|`clearError(deviceId)`|`clear_error(device_id)`|
|重启|`rebootDevice(channel, deviceId, mode)`|`reboot(device_id, mode)`|
|恢复出厂|`restore(deviceId)`|`restore(device_id)`|



## 文档修订记录

|**修改时间**|**版本**|**修改内容**|
|---|---|---|
|2026\.10\.30|V1\.0|编写 Python 版用户接口说明|
|2026\.11\.06|V1\.1|新增 home\_fingers/home\_thumb、get\_enable\_status、用户自定义表接口；补充上电回零要求|
|2026\.11\.18|V1\.2|修改用户自定表参数类型，改为填写指定的字段码；|



