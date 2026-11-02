---
tags: [物理AI, ROS2, micro-ROS, 系统集成]
prerequisites: [06-机器人通信总线]
---

# ROS 2 与 MCU 协同

## 职责边界

### MCU 保留

- 电机电流/速度/位置内环。
- 高速采样、编码器、PWM 和硬件保护。
- 通信超时后的本地安全状态。
- 启动自检、看门狗和急停链路。

### ROS 2 / Linux 负责

- 视觉与高算力推理。
- 建图、定位、路径和任务规划。
- 多节点组合、记录、可视化和远程运维。

## 接入方式

- 自定义串口/CAN 协议 + ROS 2 bridge：容易控制资源和故障语义。
- micro-ROS：让 MCU 以 ROS 2 实体参与系统，但要评估内存、传输和实时边界。
- 驱动器自带 CAN/EtherCAT 等工业接口：按设备生态集成。

## ROS 2 接口设计

- Topic 适合连续数据流；Service 适合短请求；Action 适合可取消的长任务。
- QoS 按数据语义选择：传感器流、命令、配置和状态不应全部使用同一配置。
- 消息使用标准单位和明确 frame；每条传感器消息保留采样时间。
- 控制命令包含有效期或序号，断联后 MCU 自主停车。

## 最小系统

```text
ROS 2 velocity command
        ↓
Linux bridge / micro-ROS agent
        ↓ UART/CAN/USB
MCU command validator → trajectory limiter → motor control
        ↑
encoder + IMU + fault state
```

## 实验

1. MCU 发布编码器/IMU 状态，上位机记录 rosbag。
2. ROS 2 发布速度目标，MCU 限幅后执行。
3. 杀死 ROS 节点或拔线，MCU 在超时内安全停车。
4. 人为增加延迟和丢包，观察命令新鲜度检查。
5. 重启任一端，协议能够重新同步而不突然动作。

官方入口见 [[物理AI官方资料索引]]。

