#ifndef DEBOUNCE_H
#define DEBOUNCE_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool stable;
    bool candidate;
    uint32_t candidate_since_ms;
    uint32_t debounce_ms;
} debounce_t;

void debounce_init(debounce_t *self, bool initial, uint32_t debounce_ms,
                   uint32_t now_ms);
bool debounce_update(debounce_t *self, bool raw, uint32_t now_ms,
                     bool *changed);

#endif

