# 从零开始的嵌入式视觉与云台相机

面向零基础、以实操为主的中文学习库。最终作品：**识别画面主体 → 两轴云台调整构图 → 评估画面 → 在硬件支持时调整曝光等参数**。

参考 [convex-optimization-notes](https://github.com/wly63227/convex-optimization-notes) 的“系统讲义 + 练习参考解 + 可复现实验 + 知识索引”组织方式重新编写。第一阶段使用现有电脑 + STM32，采购总计划 **480 元（含 100 元预留，非实时市场报价）**；后期再迁移到树莓派。

## 从这里开始

1. [学习指南](docs/camera/guide.md)：零基础顺序、项目分工和学习方法。
2. [硬件采购与接线](docs/camera/hardware.md)：现在买、之后买、暂时不买；逐项额度、型号条件、接线。
3. [第 00 课：无需硬件的首次运行](docs/camera/00-start.md)。
4. [20 周学习计划](docs/camera/syllabus.md) 与 [实操实验册](docs/camera/labs.md)。
5. [整合学习笔记](嵌入式视觉与云台相机学习笔记.md)：同一份正文生成，便于连续阅读。

## 课程目录

| 阶段 | 讲义 | 你会做出的东西 |
|---|---|---|
| 0 | [00 首次运行](docs/camera/00-start.md) | 无硬件构图模拟与 CSV |
| 1 | [01 电学与接线](docs/camera/01-electricity.md) | 供电、万用表、LED 回路 |
| 2 | [02 C 语言](docs/camera/02-c.md) | 限幅、类型、数组与时间差 |
| 3 | [03 编译烧录](docs/camera/03-toolchain.md) | 第一个 CubeIDE 工程与断点 |
| 4 | [04 GPIO 与时间](docs/camera/04-gpio-time.md) | 不阻塞的闪灯与按键消抖 |
| 5 | [05 PWM 与舵机](docs/camera/05-pwm.md) | 单轴到双轴、方向与范围标定 |
| 6 | [06 串口协议](docs/camera/06-protocol.md) | 校验、序号、300 ms 超时停机 |
| 7 | [07 Python 与相机](docs/camera/07-python-camera.md) | 视频采集、数组与正确退出 |
| 8 | [08 视觉检测](docs/camera/08-vision.md) | HSV 绿色目标定位与失败样本 |
| 9 | [09 构图与控制](docs/camera/09-control-composition.md) | 居中/三分点，限速、死区 |
| 10 | [10 拍摄参数](docs/camera/10-photography.md) | 曝光能力表、主体 ROI 质量评估 |
| 11 | [11 模式识别](docs/camera/11-recognition.md) | 正脸检测基线、数据划分、P/R |
| 12 | [12 联调](docs/camera/12-integration.md) | 故障注入与毕业演示 |
| 13 | [13 边缘设备（后期）](docs/camera/13-edge.md) | 树莓派、CSI、曝光元数据 |

配套：[知识清单](docs/camera/knowledge.md) · [习题](docs/camera/exercises.md) · [参考解](docs/camera/answers.md) · [实验记录](docs/camera/learning-log.md) · [排错](docs/camera/troubleshooting.md) · [术语](docs/camera/glossary.md) · [官方资料](docs/camera/sources.md)。

## 先运行，不急着买齐

在仓库根目录执行，Python 3.12+；以下无需额外依赖：

```powershell
python examples/camera_tracker/simulate.py
python -m unittest discover -s tests -v
```

真实摄像头安装依赖后运行，默认仅预览：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-camera.txt
.\.venv\Scripts\python.exe examples/camera_tracker/live.py --camera 0
```

明确提供 `--port COM号` 才输出舵机指令。先完成 [固件接入与板上验收](firmware/stm32_gimbal/README.md)，再连接负载。[程序说明](examples/camera_tracker/README.md) 包含完整命令与边界。

## 项目状态

已提供讲义、实验、绿色/正脸视觉基线、构图控制器、模拟、串口协议、可移植 C 云台模块和 HAL 适配示例。软件验证记录见 [validation.json](results/validation.json)。

**需要实物验证：** CubeIDE/HAL 集成、供电峰值、波形、机械范围、真实视觉表现、实际相机参数执行。没有把模拟结果当作实测性能。便宜 USB 相机不保证可控曝光或对焦；树莓派路线为后续升级。微舵机原型只承载轻型模块，不能直接托举真实相机。

## 维护与扩展

```powershell
python tools/check_links.py
python tools/build_camera_book.py
```

`docs/camera/` 是新课程唯一正文，整合笔记由脚本生成。GitHub Actions 检查 Python、C 应用和文档链接。现有通用课程与物理 AI 笔记保留为 [补充学习库](README-general.md)，之后可补 ADC/DMA、总线、FreeRTOS 与 ROS 2。

[发布说明](PUBLISH.md)。课程自编文本和代码按 [MIT](LICENSE) 提供；第三方手册、软件和模型遵循原许可。
