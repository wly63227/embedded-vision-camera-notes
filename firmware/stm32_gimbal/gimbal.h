#ifndef GIMBAL_H
#define GIMBAL_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Implement these two hooks in the HAL adapter. Must not block. */
void gimbal_hw_write(uint16_t pan_us, uint16_t tilt_us);
void gimbal_hw_disable(void);

typedef struct {
    bool armed, active, seq_seen, discarding;
    uint16_t seq, target_pan, target_tilt;
    float pan, tilt;
    uint32_t last_valid_ms, last_tick_ms;
    char line[64];
    size_t used;
} Gimbal;

void gimbal_init(Gimbal *g, uint32_t now_ms);
void gimbal_stop(Gimbal *g);
void gimbal_tick(Gimbal *g, uint32_t now_ms);
void gimbal_feed(Gimbal *g, char byte, uint32_t now_ms);
#endif
