# NUCLEO-F401RE 两轴云台应用模块

这是应用源码与 HAL 接入示例，不是包含 HAL、启动文件和链接脚本的完整烧录工程。电脑测试只覆盖可移植状态与解析器；HAL 适配、引脚、电源和实际运动需按下表板上验收。

## CubeIDE 配置

1. Board Selector 选 NUCLEO-F401RE，记录 CubeIDE 和 STM32CubeF4 版本；保留 SWD。
2. USART2 异步，115200、8N1，PA2/PA3；查 UM1724 确认板载 ST-LINK 虚拟串口焊桥连接。
3. PA0 配 TIM2_CH1，PA1 配 TIM2_CH2；两通道 PWM mode 1、高有效。
4. 时钟树核实 APB1 timer clock。若为 84 MHz，PSC=83、ARR=19999；若不同，按课程公式重新计算，确保一计数为 1 μs。
5. 初始 CCR=1500；生成代码后不在其他位置调用 PWM Start。
6. 把 `gimbal.c`、`hal_adapter.c` 放 Core/Src，`gimbal.h` 放 Core/Inc。
7. `main.c` USER CODE PV 区声明 `void CameraGimbal_Init(void); void CameraGimbal_Poll(void);`。
8. 所有 `MX_..._Init()` 之后，在 USER CODE 2 区调用 `CameraGimbal_Init();`；主循环 USER CODE 3 区调用 `CameraGimbal_Poll();`。不加入 HAL_Delay 或长耗时工作。
9. 编译并检查警告；保存 `.ioc` 到自己的实验记录。先不接舵机，测量 PA0、PA1 波形。

默认脉宽范围 1200～1800 μs、最大变化速度 120 μs/s。调整边界时要同时修改 Python 编码、控制器和 C 解析器，并重新运行测试；边界以实际机械校准为准。

## 协议和失效行为

见 [第 06 课](../../docs/camera/06-protocol.md)。只接受 LF 换行，串口工具请选择 LF，CRLF 会被视为非法控制字符并停机。无效格式与校验失败会停机锁存；重复或旧序号被忽略，也不刷新 300 ms 超时。

开机等待合法 P、PWM 关闭；STOP/超时/超长行/控制字符/串口错误会停脉冲。ARM 清除锁存并重置序号，但不启动输出。ARM 后从中位 1500 μs 重新开始，实际机构若已偏离中位，重新上电仍可能产生转动，必须脱载或确保中位机械可达。

HAL polling 方案只适用于短教学程序。增加图像之外的 MCU 任务后，应改用 IRQ/DMA 与正确的单生产者环形缓冲区，并增加溢出策略；不要通过放大看门超时掩盖阻塞。

## 必做板上验收

| 项目 | 预期 |
|---|---|
| 上电、仅 ARM | 两路无 PWM 输出 |
| 合法递增 P | 50 Hz，脉宽受软件限幅与变化速度限制 |
| STOP、坏校验、超长行 | 输出取消，P 不能自行恢复 |
| 数据线断开、主机冻结 | 最后合法帧约 300 ms 后取消输出（用仪器实测容差） |
| 序号 65535→0 | 在同一会话中正常接收 |
| 重放旧帧 | 不刷新超时 |
| 两轴同时运动 | 电源不塌陷、MCU 不重启、机械不顶死 |

取消 PWM 可能导致卸力下垂；支架必须稳定，独立电源开关可触及。调试 CPU 停住时软件看门不能继续运行，连接负载时不可依赖断点下的软件停机保证。
