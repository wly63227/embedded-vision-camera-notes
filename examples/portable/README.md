# 可移植 C 组件

这些例子不调用 STM32 HAL 或 ESP-IDF，可先在电脑上验证，再通过 BSP 接入开发板。

## 构建

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

内容：

- `debounce.*`：支持毫秒计数回绕的按键消抖器。
- `ring_buffer.*`：固定容量字节环形缓冲区，满时拒绝新数据。
- `state_machine.*`：显式设备状态和错误降级示例。
- `test_main.c`：无第三方依赖的基础测试。

实际中断环境中使用环形缓冲区时，还要根据生产者/消费者模型和目标架构设计原子性与临界区；当前实现用于讲解数据结构和主机测试，不宣称自动具备线程安全性。

