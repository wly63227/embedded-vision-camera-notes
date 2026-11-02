# 13｜后续升级：独立相机与边缘识别

**前置：** V1 完成，确认自己需要独立运行。**硬件：** 后期采购，不计入首批 300～500 元。

## 为什么此时才买树莓派

电脑上已经验证检测、构图和协议后，再把上位机迁到 Linux，可以把问题限定在环境、设备和算力差异。建议树莓派 5 的内存配置按模型需要选择，配匹配电源、散热、存储卡、Camera Module 3 标准版和 Pi 5 适配的 22-pin 到 15-pin 摄像头线。不要用 Pi 4 套件线默认替代。MCU 和舵机供电仍按原设计分开。

Camera Module 3 支持自动对焦，固定光圈；软件能控制什么要以实际 `camera_controls` 为准。树莓派 CSI 相机不能直接接 STM32 普通 GPIO。

## 先做一次受控曝光实验

使用与当前 Raspberry Pi OS 匹配的官方 Picamera2 安装方式。以下仅为设备端实验，不在普通 Windows 上运行：

```python
from picamera2 import Picamera2
from time import sleep

cam = Picamera2()
cam.configure(cam.create_still_configuration())
print(cam.camera_controls)
cam.start()
try:
    cam.set_controls({'AeEnable': False,
                      'ExposureTime': 10000,
                      'AnalogueGain': 1.0})
    sleep(1)  # 本课静态能力实验，给传感器控制生效时间
    print(cam.capture_metadata())
    cam.capture_file('manual-exposure.jpg')
finally:
    cam.stop()
```

`ExposureTime` 单位是微秒，`AnalogueGain` 是倍率。10000 μs 只是示例，须落在当前配置允许范围内；帧时长也约束曝光。控制改变可能延后多帧生效，必须读元数据验证实际值。相机 API 的细节以 [官方手册](sources.md) 为准。

## 构图与拍摄策略一起工作

先固定曝光做云台控制，等画面位置稳定；再每 0.5～1 秒评估主体 ROI，按小步长调整曝光，等待稳定后拍摄。不要在舵机快速转动时反复调整对焦和快门，再把运动模糊误判成失焦。

更完整的状态机可以是：发现主体 → 稳定身份 → 移动构图 → 稳定等待 → 调曝光/对焦 → 验证清晰 → 拍摄 → 重新检测。每步有最大等待时间、失败回退和日志。

## 实操 L13 与进阶路线

先比较同一段视频在电脑与树莓派上的处理耗时、内存和漏检；然后验证实际相机的三档曝光。只有能够复现元数据变化与画面变化，才接入自动策略。下一步再学轻量模型训练、量化、ONNX 或设备对应推理运行时，测延迟与精度变化。

先不引入 ROS 2、SLAM、无人机和三轴无刷电机。若之后要托举真实相机，需重新设计载荷、轴承、重心、反馈编码器和电机驱动，并单独验算；微舵机实验的采购不能直接升级承载。

E13：自动曝光刚关闭后第一帧的元数据仍是旧值，程序应该如何决定它是否能用于闭环判断？
