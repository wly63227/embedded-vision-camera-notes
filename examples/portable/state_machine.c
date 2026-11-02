#include "state_machine.h"

#include <stddef.h>

static void transition(device_t *self, device_state_t next, uint32_t now_ms) {
    self->state = next;
    self->entered_at_ms = now_ms;
}

void device_init(device_t *self, uint32_t now_ms) {
    if (self == NULL) {
        return;
    }
    self->state = DEVICE_BOOT;
    self->consecutive_failures = 0U;
    self->entered_at_ms = now_ms;
}

bool device_dispatch(device_t *self, device_event_t event, uint32_t now_ms) {
    if (self == NULL) {
        return false;
    }
    if (event == EVENT_FATAL) {
        transition(self, DEVICE_ERROR, now_ms);
        return true;
    }

    switch (self->state) {
    case DEVICE_BOOT:
        if (event == EVENT_TICK) {
            transition(self, DEVICE_SELF_TEST, now_ms);
            return true;
        }
        break;
    case DEVICE_SELF_TEST:
        if (event == EVENT_SELF_TEST_OK) {
            transition(self, DEVICE_RUN, now_ms);
            return true;
        }
        break;
    case DEVICE_RUN:
        if (event == EVENT_SENSOR_FAILED) {
            self->consecutive_failures++;
            if (self->consecutive_failures >= 3U) {
                transition(self, DEVICE_DEGRADED, now_ms);
            }
            return true;
        }
        if (event == EVENT_SENSOR_RECOVERED) {
            self->consecutive_failures = 0U;
            return true;
        }
        break;
    case DEVICE_DEGRADED:
        if (event == EVENT_SENSOR_RECOVERED) {
            self->consecutive_failures = 0U;
            transition(self, DEVICE_RUN, now_ms);
            return true;
        }
        break;
    case DEVICE_ERROR:
    default:
        break;
    }
    return false;
}

