# 来源与版本说明

核对日期：2026-11-02。文字、例题与实验为本库自编；硬件行为以**手中实际型号、板卡版本、数据手册、驱动和配置**为准。预算表给采购额度，没有声称查到了当前电商成交价。

| 官方来源 | 用来确认什么 | 对应讲义 |
|---|---|---|
| [ST NUCLEO-F401RE 产品页](https://www.st.com/en/evaluation-tools/nucleo-f401re.html) | 开发板类型、板载调试器、文档入口 | 03、采购 |
| [ST UM1724 Nucleo-64 用户手册](https://www.st.com/resource/en/user_manual/dm00105823-nucleo-f401re-user-manual-stmicroelectronics.pdf) | 板级连接、ST-LINK/VCP、接线与供电 | 01、03、05、06 |
| [STM32F401 参考手册 RM0368](https://www.st.com/resource/en/reference_manual/rm0368-stm32f401xbc-and-stm32f401xde-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) | 时钟树、定时器、GPIO、UART 寄存器 | 04～06 |
| [STM32CubeIDE](https://www.st.com/en/development-tools/stm32cubeide.html) | 官方工具下载与当前安装说明 | 03 |
| [Python 官方入门](https://docs.python.org/zh-cn/3/tutorial/) | Python 语法、模块和基础概念 | 00、07 |
| [Python venv](https://docs.python.org/3/library/venv.html) | 隔离项目环境 | 07 |
| [Git 官方下载](https://git-scm.com/downloads) | Git 获取入口 | 00 |
| [OpenCV HSV inRange 教程](https://docs.opencv.org/4.x/da/d97/tutorial_threshold_inRange.html) | 颜色范围分割 | 08 |
| [OpenCV Moments 文档](https://docs.opencv.org/4.x/d8/d23/classcv_1_1Moments.html) | 区域矩与质心定义 | 08 |
| [OpenCV Video I/O 属性](https://docs.opencv.org/4.x/d4/d15/group__videoio__flags__base.html) | 属性受设备、驱动与后端影响 | 07、10 |
| [OpenCV 级联分类教程](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html) | Haar 级联检测基线 | 11 |
| [pySerial API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html) | 串口超时、读写行为 | 06、12 |
| [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/) | 自动对焦、相机规格 | 13 |
| [Raspberry Pi 相机硬件](https://www.raspberrypi.com/documentation/accessories/camera.html) | 相机接口与排线适配 | 13、后期采购 |
| [Picamera2 官方手册](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf) | 控制、参数单位、元数据与生效延迟 | 10、13 |

软件依赖在 `requirements-camera.txt` 中约束主版本范围；本次实际运行版本写入 [验证记录](../../results/validation.json)。后续重装得到不同补丁版本时重新运行测试，记录差异。ST HAL 与 Cube 工程需要用户按实板生成，本库没有把未编译的 HAL 适配声称为板上验证成功。

本库没有复制厂商手册或凸优化 PDF，也不为第三方文档或 OpenCV 随附模型重新授予许可证。跟随第三方软件与模型各自的许可要求。
