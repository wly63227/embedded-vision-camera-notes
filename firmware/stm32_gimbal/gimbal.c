#include "gimbal.h"
#include <string.h>

static bool decimal(const char *s, size_t n, uint16_t *out) {
    uint32_t value = 0;
    if (n == 0 || n > 5 || (n > 1 && s[0] == '0')) return false;
    for (size_t i = 0; i < n; ++i) {
        if (s[i] < '0' || s[i] > '9') return false;
        value = value * 10u + (uint32_t)(s[i] - '0');
    }
    if (value > 65535u) return false;
    *out = (uint16_t)value;
    return true;
}

static int hex_digit(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static bool parse_position(const char *line, uint16_t *seq, uint16_t *pan, uint16_t *tilt) {
    size_t length = strlen(line), commas[4], count = 0;
    if (length < 3 || line[0] != 'P' || line[1] != ',') return false;
    for (size_t i = 0; i < length; ++i) {
        if (line[i] == ',') {
            if (count == 4) return false;
            commas[count++] = i;
        }
    }
    if (count != 4 || commas[0] != 1 || length - commas[3] != 3) return false;
    int high = hex_digit(line[commas[3] + 1]), low = hex_digit(line[commas[3] + 2]);
    if (high < 0 || low < 0) return false;
    uint8_t checksum = 0;
    for (size_t i = 0; i < commas[3]; ++i) checksum ^= (uint8_t)line[i];
    if (checksum != (uint8_t)(high * 16 + low)) return false;
    if (!decimal(line + commas[0] + 1, commas[1] - commas[0] - 1, seq) ||
        !decimal(line + commas[1] + 1, commas[2] - commas[1] - 1, pan) ||
        !decimal(line + commas[2] + 1, commas[3] - commas[2] - 1, tilt)) return false;
    return *pan >= 1200 && *pan <= 1800 && *tilt >= 1200 && *tilt <= 1800;
}

void gimbal_stop(Gimbal *g) {
    g->armed = false;
    g->active = false;
    gimbal_hw_disable();
}

void gimbal_init(Gimbal *g, uint32_t now_ms) {
    memset(g, 0, sizeof(*g));
    g->armed = true; /* ready to receive first command, outputs still disabled */
    g->pan = g->tilt = 1500.0f;
    g->target_pan = g->target_tilt = 1500;
    g->last_tick_ms = now_ms;
    gimbal_hw_disable();
}

static void handle_line(Gimbal *g, uint32_t now_ms) {
    if (strcmp(g->line, "STOP") == 0) {
        gimbal_stop(g);
        return;
    }
    if (strcmp(g->line, "ARM") == 0) {
        /* Re-arm never energizes a servo. Session and target are reset. */
        gimbal_stop(g);
        g->armed = true;
        g->seq_seen = false;
        g->pan = g->tilt = 1500.0f;
        g->target_pan = g->target_tilt = 1500;
        g->last_tick_ms = now_ms;
        return;
    }
    uint16_t seq, pan, tilt;
    if (!parse_position(g->line, &seq, &pan, &tilt)) {
        gimbal_stop(g);
        return;
    }
    if (!g->armed) return;
    if (g->seq_seen) {
        uint16_t delta = (uint16_t)(seq - g->seq);
        if (delta == 0 || delta >= 32768u) return;
    }
    g->seq = seq;
    g->seq_seen = true;
    g->target_pan = pan;
    g->target_tilt = tilt;
    g->last_valid_ms = now_ms;
    g->active = true;
}

void gimbal_feed(Gimbal *g, char byte, uint32_t now_ms) {
    /* Check timeout BEFORE accepting a packet after a prolonged gap. */
    gimbal_tick(g, now_ms);
    if (byte == '\n') {
        if (!g->discarding) {
            g->line[g->used] = '\0';
            handle_line(g, now_ms);
        }
        g->used = 0;
        g->discarding = false;
        return;
    }
    if (g->discarding) return;
    if (byte < 32 || byte > 126 || g->used >= sizeof(g->line) - 1) {
        gimbal_stop(g);
        g->discarding = true;
        g->used = 0;
        return;
    }
    g->line[g->used++] = byte;
}

static float approach(float current, float target, float step) {
    if (target > current + step) return current + step;
    if (target < current - step) return current - step;
    return target;
}

void gimbal_tick(Gimbal *g, uint32_t now_ms) {
    uint32_t elapsed = now_ms - g->last_tick_ms;
    g->last_tick_ms = now_ms;
    if (!g->active || !g->armed) return;
    if ((uint32_t)(now_ms - g->last_valid_ms) >= 300u) {
        gimbal_stop(g);
        return;
    }
    if (elapsed > 100u) elapsed = 100u;
    float step = 0.12f * (float)elapsed; /* 120 us/s maximum */
    g->pan = approach(g->pan, (float)g->target_pan, step);
    g->tilt = approach(g->tilt, (float)g->target_tilt, step);
    gimbal_hw_write((uint16_t)(g->pan + 0.5f), (uint16_t)(g->tilt + 0.5f));
}
