#include "ring_buffer.h"

bool ring_buffer_init(ring_buffer_t *self, uint8_t *storage, size_t capacity) {
    if ((self == NULL) || (storage == NULL) || (capacity == 0U)) {
        return false;
    }
    self->data = storage;
    self->capacity = capacity;
    self->head = 0U;
    self->tail = 0U;
    self->count = 0U;
    return true;
}

bool ring_buffer_push(ring_buffer_t *self, uint8_t value) {
    if ((self == NULL) || (self->count == self->capacity)) {
        return false;
    }
    self->data[self->head] = value;
    self->head = (self->head + 1U) % self->capacity;
    self->count++;
    return true;
}

bool ring_buffer_pop(ring_buffer_t *self, uint8_t *value) {
    if ((self == NULL) || (value == NULL) || (self->count == 0U)) {
        return false;
    }
    *value = self->data[self->tail];
    self->tail = (self->tail + 1U) % self->capacity;
    self->count--;
    return true;
}

size_t ring_buffer_size(const ring_buffer_t *self) {
    return (self == NULL) ? 0U : self->count;
}

