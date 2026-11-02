---
tags: [物理AI, 参考资料, 官方文档]
---

# 物理 AI 官方资料索引

返回：[[00-物理AI嵌入式学习地图]]

## MCU 与实时系统

- [STM32 入门步骤](https://wiki.st.com/stm32mcu/wiki/STM32StepByStep:STM32_step_by_step_overview)
- [STM32Cube 文档中心](https://dev.st.com/stm32cube-docs/)
- [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/)
- [FreeRTOS Documentation](https://www.freertos.org/Documentation/00-Overview)
- [Zephyr Sensors](https://docs.zephyrproject.org/latest/hardware/peripherals/sensor/index.html)

## Arm 与边缘 AI

- [CMSIS 总览](https://arm-software.github.io/CMSIS_6/latest/General/index.html)
- [CMSIS-DSP](https://arm-software.github.io/CMSIS-DSP/latest/)
- [CMSIS-NN](https://arm-software.github.io/CMSIS-NN/latest/)
- [TensorFlow Lite for Microcontrollers](https://ai.google.dev/edge/litert/microcontrollers/overview)
- [Edge Impulse Documentation](https://docs.edgeimpulse.com/docs)

## ROS 2 与嵌入式协同

- [ROS 2 Documentation](https://docs.ros.org/en/rolling/)
- [ROS 2 Releases](https://docs.ros.org/en/rolling/Releases.html)
- [micro-ROS Documentation](https://micro.ros.org/docs/)

学习时优先使用当前受支持的 ROS 2 发行版，不要把 Rolling 的实验性变化当成稳定接口。

## 阅读方法

1. 先读开发板原理图和芯片数据手册，确认电压、引脚和限制。
2. 用参考手册查外设行为，用勘误表检查已知硬件问题。
3. 工具或库 API 以对应版本的官方文档为准。
4. 把关键时序、范围和错误条件写成断言或测试，而不是只放在笔记里。

