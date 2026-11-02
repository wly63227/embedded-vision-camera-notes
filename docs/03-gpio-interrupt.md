# 03｜GPIO、中断与按键消抖

## GPIO 配置

GPIO 常见模式包括输入、推挽输出、开漏输出、模拟和复用功能。输入可能需要内部上拉/下拉；开漏总线通常需要外部上拉。驱动能力和翻转速度越高不一定越好，过快边沿会增加干扰和功耗。

## 中断模型

外部事件产生中断请求，NVIC 根据使能、优先级和当前执行状态决定何时进入 ISR。ISR 应短小、确定、不可阻塞：

```c
void button_exti_callback(void) {
    button_edge_pending = true;  // 记录事件
}

int main(void) {
    for (;;) {
        if (button_edge_pending) {
            button_edge_pending = false;
            button_process(get_tick_ms(), read_button_pin());
        }
    }
}
```

共享多字节对象时，`volatile` 不足以保证一致性。可用临界区、原子操作、单生产者/单消费者结构，或 RTOS 同步原语。

## 消抖

机械按键一次动作会产生多次快速跳变。常见方案：

- 延时后再读：简单但阻塞，不适合作为最终架构。
- 定时采样：连续 N 次一致后改变稳定状态。
- 时间戳状态机：电平变化后保持一段时间再确认。

参考 `examples/portable/debounce.c`。注意消抖解决的是抖动，不等于短按、长按、双击等高层手势识别。

## 实验：非阻塞按键控制器

功能：短按切换 LED，长按 1 秒进入呼吸模式。主循环不得使用超过 1 ms 的阻塞延时。

分层建议：

- `bsp_button_read()`：读取物理电平并转换为逻辑按下/释放。
- `debounce_update()`：得到稳定边沿。
- `button_gesture_update()`：识别短按/长按。
- `app_handle_event()`：改变应用状态。

## 验收标准

- 快速连续按 30 次，每次只触发一次。
- 长按期间主循环仍可处理串口。
- ISR 中没有打印、动态分配或长循环。
- 能解释有效低按键为何要做逻辑归一化。

