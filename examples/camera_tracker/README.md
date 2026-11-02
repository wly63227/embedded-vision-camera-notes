# 云台构图示例

从 [课程入口](../../docs/camera/guide.md) 学习。默认不打开串口，必须明确传入 `--port` 才会输出控制。只适合桌面轻型位置舵机原型。

## 无硬件、无第三方依赖

在仓库根目录执行：

```powershell
python examples/camera_tracker/simulate.py
python examples/camera_tracker/simulate.py --target-x 0.333333
python -m unittest discover -s tests -v
```

没有 OpenCV 时，图像测试会明确跳过；核心控制与协议仍运行。模拟最后会隐藏目标，进入 STOP；它只展示算法行为，不证明实物精度、时延或负载能力。

## 真实摄像头，默认只预览

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-camera.txt
.\.venv\Scripts\python.exe examples/camera_tracker/live.py --camera 0
.\.venv\Scripts\python.exe examples/camera_tracker/live.py --detector face
.\.venv\Scripts\python.exe examples/camera_tracker/camera_probe.py --camera 0
.\.venv\Scripts\python.exe examples/camera_tracker/quality.py --self-test
```

face 模式使用 OpenCV 软件包自带正脸级联，不做人脸身份识别；没有额外权重下载。绿色阈值在 `live.py` 中集中设置。多目标时选最大框，暂未提供稳定身份跟踪。

## 接真实云台

先按 [接线](../../docs/camera/hardware.md) 与 [固件配置](../../firmware/stm32_gimbal/README.md) 验证。脱载标定两轴 sign，实测限位。示例串口名和方向不能照抄：

```powershell
.\.venv\Scripts\python.exe examples/camera_tracker/live.py --camera 0 --port COM5 --pan-sign 1 --tilt-sign -1 --max-rate 60
```

启动先发 STOP、ARM；q、空格、Esc 或退出会尝试 STOP；目标丢失超过 300 ms 后锁存停止，需要人工检查再运行。USB 断开靠 MCU 自己的 300 ms 超时取消 PWM。输出取消可能卸力，机构需要支撑。

## 文件说明与已知边界

| 文件 | 功能 |
|---|---|
| core.py | 无依赖比例控制、限速、限幅、目标缺失锁存；XOR 帧编码 |
| simulate.py | 简化画面位置模型与 CSV，非物理仿真 |
| live.py | 绿色/正脸检测 → 构图 → 可选串口；无曝光自动写入 |
| camera_probe.py | 读取后端属性，可选按驱动单位请求曝光；不会自动切换 AE |
| quality.py | 灰度中位数、高亮比例、清晰度代理；只产生建议 |
| histogram_classifier.py | 颜色直方图训练/测试与混淆矩阵；不定位、不提供未知类拒识 |

日志时间是电脑 monotonic 接收/处理时间，不是传感器曝光时间戳。相机驱动缓存仍可能产生旧帧，当前接口不能跨后端证明帧龄；上线前做外部端到端延迟测量，必要时改为可提供时间戳的采集 API。协议当前没有 ACK，串口写入成功不表示 MCU 执行成功。

Python 最终精确版本与实际检查结果保存在 [验收记录](../../results/validation.json)。实机视觉效果、HAL 集成和机械行为需要自己完成 [实验册](../../docs/camera/labs.md)。
