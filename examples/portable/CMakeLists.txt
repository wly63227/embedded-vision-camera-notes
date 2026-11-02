cmake_minimum_required(VERSION 3.16)
project(portable_embedded_examples C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(portable_tests
    debounce.c
    ring_buffer.c
    state_machine.c
    test_main.c
)

if(MSVC)
    target_compile_options(portable_tests PRIVATE /W4)
else()
    target_compile_options(portable_tests PRIVATE
        -Wall -Wextra -Wpedantic -Wconversion
    )
endif()

enable_testing()
add_test(NAME portable_tests COMMAND portable_tests)

