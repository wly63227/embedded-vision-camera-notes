# 01｜面向嵌入式的 C 语言

## 必须掌握的知识

### 数据类型与边界

优先使用 `<stdint.h>` 中的 `uint8_t`、`int16_t`、`uint32_t` 等定宽类型。涉及长度和数组下标时使用 `size_t`。不要假设 `int` 固定为 32 位，也不要混用有符号和无符号数。

```c
#include <stdint.h>

uint16_t raw_adc;
int32_t temperature_milli_c;   // 以 0.001 ℃ 为单位，避免浮点
```

### 位操作

寄存器和协议字段都依赖位操作：

```c
#define BIT(n) (1UL << (n))

reg |= BIT(3);          // 置位
reg &= ~BIT(3);         // 清零
reg ^= BIT(3);          // 翻转
bool set = (reg & BIT(3)) != 0U;
reg = (reg & ~(0x7UL << 4)) | ((value & 0x7UL) << 4); // 更新位域
```

位移前确认宽度；对可能超出范围的移位进行约束。宏参数要加括号，复杂逻辑优先用 `static inline` 函数。

### 指针、数组与生命周期

- 数组在多数表达式中会退化为指向首元素的指针，但数组和指针不是同一个对象。
- 不返回局部变量地址；不要越界；传数组时同时传长度。
- 指针解引用前确认有效性、对齐和对象生命周期。
- 字符串以 `\0` 结束；二进制缓冲区不能依赖字符串函数。

### `const`、`volatile` 与 `static`

- `const`：通过此名字不修改对象，常用于只读参数和查找表。
- `volatile`：对象可能被中断、DMA 或硬件改变，要求每次实际访问；它**不提供原子性，也不解决线程同步**。
- 文件级 `static`：限制符号可见范围；函数内 `static`：对象在整个程序期间存在。

```c
static volatile bool uart_rx_ready;

void uart_irq_handler(void) {
    uart_rx_ready = true;
}
```

### 结构体与模块化

每个模块至少包含：公开头文件、私有实现、初始化、输入/输出接口、错误返回值。避免让所有模块直接访问全局变量。

```c
typedef enum {
    SENSOR_OK = 0,
    SENSOR_ERR_ARG,
    SENSOR_ERR_BUS,
    SENSOR_ERR_TIMEOUT
} sensor_status_t;

sensor_status_t sensor_read(sensor_t *self, sensor_sample_t *out);
```

## 编译与链接心智模型

预处理器展开头文件和宏；编译器把每个 `.c` 变成目标文件；链接器解析符号并按链接脚本放入 Flash/RAM。遇到 `undefined reference` 先检查实现文件是否参与构建；遇到 `multiple definition` 先检查是否在头文件中定义了非 `static` 对象。

## 练习

1. 实现 `set_field(value, mask, shift, field)`，只更新指定位域。
2. 实现饱和加法：超过上限返回上限，不允许无符号回绕。
3. 实现长度受限的字节序转换函数。
4. 编译并测试 `examples/portable/` 中的状态机、消抖器和环形缓冲区。

## 验收标准

- 开启 `-Wall -Wextra -Wconversion` 后没有未解释的警告。
- 能从 `.map` 文件找到函数和全局变量所在段。
- 能解释为什么 `volatile uint32_t counter++` 不是原子操作。
- 每个接口都明确参数有效范围、返回值和调用上下文。

