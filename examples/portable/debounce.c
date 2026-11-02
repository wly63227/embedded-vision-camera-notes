#include "debounce.h"

#include <stddef.h>

void debounce_init(debounce_t *self, bool initial, uint32_t debounce_ms,
                   uint32_t now_ms) {
    if (self == NULL) {
        return;
    }
    self->stable = initial;
    self->candidate = initial;
    self->candidate_since_ms = now_ms;
    self->debounce_ms = debounce_ms;
}

bool debounce_update(debounce_t *self, bool raw, uint32_t now_ms,
                     bool *changed) {
    if ((self == NULL) || (changed == NULL)) {
        return false;
    }
    *changed = false;

    if (raw != self->candidate) {
        self->candidate = raw;
        self->candidate_since_ms = now_ms;
    }

    if ((self->candidate != self->stable) &&
        ((uint32_t)(now_ms - self->candidate_since_ms) >= self->debounce_ms)) {
        self->stable = self->candidate;
        *changed = true;
    }
    return self->stable;
}

