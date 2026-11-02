#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    DEVICE_BOOT = 0,
    DEVICE_SELF_TEST,
    DEVICE_RUN,
    DEVICE_DEGRADED,
    DEVICE_ERROR
} device_state_t;

typedef enum {
    EVENT_TICK = 0,
    EVENT_SELF_TEST_OK,
    EVENT_SENSOR_FAILED,
    EVENT_SENSOR_RECOVERED,
    EVENT_FATAL
} device_event_t;

typedef struct {
    device_state_t state;
    uint8_t consecutive_failures;
    uint32_t entered_at_ms;
} device_t;

void device_init(device_t *self, uint32_t now_ms);
bool device_dispatch(device_t *self, device_event_t event, uint32_t now_ms);

#endif

