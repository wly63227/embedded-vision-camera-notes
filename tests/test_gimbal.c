#include "gimbal.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static bool output_enabled;
static uint16_t output_pan, output_tilt;
void gimbal_hw_write(uint16_t pan, uint16_t tilt) {
    output_enabled = true;
    output_pan = pan;
    output_tilt = tilt;
    assert(pan >= 1200 && pan <= 1800 && tilt >= 1200 && tilt <= 1800);
}
void gimbal_hw_disable(void) { output_enabled = false; }

static void feed(Gimbal *g, const char *line, uint32_t now) {
    for (size_t i = 0; line[i]; ++i) gimbal_feed(g, line[i], now);
}
static void position(Gimbal *g, unsigned seq, unsigned pan, unsigned tilt, uint32_t now) {
    char body[64], frame[80];
    snprintf(body, sizeof(body), "P,%u,%u,%u", seq, pan, tilt);
    unsigned check = 0;
    for (size_t i = 0; body[i]; ++i) check ^= (unsigned char)body[i];
    snprintf(frame, sizeof(frame), "%s,%02X\n", body, check);
    feed(g, frame, now);
}

int main(void) {
    Gimbal g;
    gimbal_init(&g, 0);
    assert(!output_enabled);
    feed(&g, "ARM\n", 0);
    assert(!output_enabled);
    position(&g, 65535, 1800, 1200, 0);
    gimbal_tick(&g, 100);
    assert(output_enabled && output_pan == 1512 && output_tilt == 1488);
    position(&g, 0, 1800, 1200, 100); /* normal wrap */
    assert(g.seq == 0 && g.last_valid_ms == 100);
    position(&g, 0, 1800, 1200, 200); /* duplicate */
    position(&g, 65535, 1800, 1200, 250); /* stale */
    assert(g.last_valid_ms == 100);
    gimbal_tick(&g, 400);
    assert(!output_enabled && !g.armed);
    position(&g, 1, 1500, 1500, 401);
    assert(!g.active);
    feed(&g, "ARM\n", 402);
    position(&g, 9, 1500, 1500, 403);
    gimbal_tick(&g, 404);
    assert(output_enabled);
    feed(&g, "P,10,1500,1500,00\n", 405); /* bad checksum */
    assert(!g.armed && !output_enabled);

    feed(&g, "ARM\n", 500);
    position(&g, 0, 1900, 1500, 501); /* good checksum, unsafe value */
    assert(!g.armed);
    feed(&g, "ARM\n", 600);
    for (int i = 0; i < 100; ++i) gimbal_feed(&g, 'X', 601);
    assert(g.discarding && !g.armed);
    feed(&g, "ARM\n", 602); /* entire overflowed line discarded */
    assert(!g.armed && !g.discarding);
    feed(&g, "ARM\n", 603);
    assert(g.armed);
    feed(&g, "STOP\n", 604);
    assert(!g.armed && !output_enabled);

    gimbal_init(&g, UINT32_MAX - 100u);
    position(&g, 0, 1800, 1500, UINT32_MAX - 100u);
    gimbal_tick(&g, 50); /* tick wrap, only 151 ms elapsed */
    assert(g.active && output_enabled);
    gimbal_tick(&g, 200); /* 301 ms */
    assert(!g.active && !output_enabled);
    puts("gimbal parser, rate, stop, replay and tick-wrap tests passed");
    return 0;
}
