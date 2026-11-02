#include "debounce.h"
#include "ring_buffer.h"
#include "state_machine.h"

#include <assert.h>
#include <stdio.h>

static void test_ring_buffer(void) {
    uint8_t storage[3];
    uint8_t value = 0U;
    ring_buffer_t rb;

    assert(ring_buffer_init(&rb, storage, 3U));
    assert(ring_buffer_push(&rb, 10U));
    assert(ring_buffer_push(&rb, 20U));
    assert(ring_buffer_push(&rb, 30U));
    assert(!ring_buffer_push(&rb, 40U));
    assert(ring_buffer_pop(&rb, &value) && value == 10U);
    assert(ring_buffer_push(&rb, 40U));
    assert(ring_buffer_size(&rb) == 3U);
}

static void test_debounce_and_wrap(void) {
    debounce_t button;
    bool changed = false;
    debounce_init(&button, false, 20U, UINT32_MAX - 10U);
    assert(!debounce_update(&button, true, UINT32_MAX - 5U, &changed));
    assert(!changed);
    assert(!debounce_update(&button, true, 5U, &changed));
    assert(debounce_update(&button, true, 15U, &changed));
    assert(changed);
}

static void test_state_machine(void) {
    device_t device;
    device_init(&device, 0U);
    assert(device_dispatch(&device, EVENT_TICK, 1U));
    assert(device.state == DEVICE_SELF_TEST);
    assert(device_dispatch(&device, EVENT_SELF_TEST_OK, 2U));
    assert(device.state == DEVICE_RUN);
    assert(device_dispatch(&device, EVENT_SENSOR_FAILED, 3U));
    assert(device_dispatch(&device, EVENT_SENSOR_FAILED, 4U));
    assert(device_dispatch(&device, EVENT_SENSOR_FAILED, 5U));
    assert(device.state == DEVICE_DEGRADED);
    assert(device_dispatch(&device, EVENT_SENSOR_RECOVERED, 6U));
    assert(device.state == DEVICE_RUN);
}

int main(void) {
    test_ring_buffer();
    test_debounce_and_wrap();
    test_state_machine();
    puts("All portable component tests passed.");
    return 0;
}

