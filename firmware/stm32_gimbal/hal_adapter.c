/* Copy to the generated CubeIDE project's Core/Src, not a standalone firmware. */
#include "main.h"
#include "gimbal.h"
extern TIM_HandleTypeDef htim2;
extern UART_HandleTypeDef huart2;
static Gimbal app;
static bool pwm_running;

void gimbal_hw_disable(void) {
    HAL_TIM_PWM_Stop(&htim2, TIM_CHANNEL_1);
    HAL_TIM_PWM_Stop(&htim2, TIM_CHANNEL_2);
    pwm_running = false;
}

void gimbal_hw_write(uint16_t pan_us, uint16_t tilt_us) {
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pan_us);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, tilt_us);
    if (!pwm_running) {
        if (HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1) != HAL_OK ||
            HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2) != HAL_OK) {
            gimbal_stop(&app);
            return;
        }
        pwm_running = true;
    }
}

void CameraGimbal_Init(void) {
    pwm_running = false;
    gimbal_init(&app, HAL_GetTick());
}

void CameraGimbal_Poll(void) {
    uint8_t byte;
    gimbal_tick(&app, HAL_GetTick());
    /* Nonblocking single-byte polling; keep the main loop free of long work. */
    if (HAL_UART_Receive(&huart2, &byte, 1, 0) == HAL_OK) {
        gimbal_feed(&app, (char)byte, HAL_GetTick());
    }
    if (HAL_UART_GetError(&huart2) != HAL_UART_ERROR_NONE) {
        /* Polling UART can overrun if other work blocks the main loop. */
        gimbal_stop(&app);
        __HAL_UART_CLEAR_OREFLAG(&huart2);
    }
}
