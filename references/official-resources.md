# 官方资料入口

优先查官方手册、示例与勘误表；博客和视频适合建立直觉，但不能替代目标芯片的文档。

## STM32

- [STM32 入门步骤](https://wiki.st.com/stm32mcu/wiki/STM32StepByStep:STM32_step_by_step_overview)
- [STM32Cube 文档中心](https://dev.st.com/stm32cube-docs/)
- [STM32CubeIDE 产品与文档](https://www.st.com/en/development-tools/stm32cubeide.html)
- [STM32 MCU 文档检索](https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus/documentation.html)

查找资料时使用芯片完整料号，并确认文档适用的系列和修订版本。

## ESP32

- [ESP-IDF Programming Guide：Get Started](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/)
- [ESP-IDF 稳定版文档入口](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/)
- [ESP-IDF 官方示例](https://github.com/espressif/esp-idf/tree/master/examples)

学习项目建议选择稳定版文档；`latest/master` 可能包含尚在开发的变化。

## Arm Cortex-M / CMSIS

- [CMSIS 文档](https://arm-software.github.io/CMSIS_6/latest/General/index.html)
- [CMSIS-Core](https://arm-software.github.io/CMSIS_6/latest/Core/index.html)

芯片厂商的参考手册描述具体外设；Arm 文档解释处理器内核、异常模型和通用接口。

## FreeRTOS

- [FreeRTOS Documentation](https://www.freertos.org/Documentation/00-Overview)
- [FreeRTOS Kernel Book](https://github.com/FreeRTOS/FreeRTOS-Kernel-Book)
- [FreeRTOS Kernel](https://github.com/FreeRTOS/FreeRTOS-Kernel)

## C 语言与安全编码

- [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard)
- 编译器手册：GCC warning、优化、链接与诊断选项。

## 高效阅读方法

1. 先用目录和搜索定位，不从第一页顺序通读参考手册。
2. 把芯片型号、文档编号和修订版本记入实验记录。
3. 同时查看开发板原理图、数据手册、参考手册和勘误表。
4. 将关键时序、位域和限制转化成代码断言或测试。

