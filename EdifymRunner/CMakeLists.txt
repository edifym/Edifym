cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)
project(EdifymRunner)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_EXTENSIONS OFF)

SET(CMAKE_SYSTEM_NAME Linux)
SET(CMAKE_SYSTEM_VERSION 1)

# specify the cross compiler
SET(CMAKE_C_COMPILER   aarch64-linux-gnu-gcc)
SET(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -s -Wl,--gc-sections -fno-stack-protector ")

if(NOT DEFINED ENV{M5_DIR})
    message(FATAL_ERROR "Please set the environment variable M5_DIR to where gem5/util/m5 is located.")
endif()

if(NOT DEFINED ENV{LIBRARY_UNDER_TEST})
    message(FATAL_ERROR "Please set the environment variable LIBRARY_UNDER_TEST to the full name of the library to be included in linking.")
endif()


add_executable(EdifymRunner main.c executable_task.h)
add_executable(StaticRunner main_static.c executable_task.h)

include_directories("$ENV{M5_DIR}/../../include")

find_library(MFIVE NAMES libm5.a HINTS $ENV{M5_DIR})
find_library(LUT NAMES $ENV{LIBRARY_UNDER_TEST} HINTS "./")

if(NOT MFIVE)
    message(FATAL_ERROR "Please compile gem5/util/m5 for aarch64 and ensure libm5.a is present in M5_DIR")
endif()

if(NOT LUT)
    message(FATAL_ERROR "Could not find LIBRARY_UNDER_TEST $ENV{LIBRARY_UNDER_TEST}")
endif()

target_link_libraries(EdifymRunner PUBLIC ${MFIVE})
target_link_libraries(EdifymRunner PUBLIC ${LUT})

set_target_properties(EdifymRunner PROPERTIES LINK_FLAGS "-static" )

target_link_libraries(StaticRunner PUBLIC ${MFIVE})
target_link_libraries(StaticRunner PUBLIC ${LUT})

set_target_properties(StaticRunner PROPERTIES LINK_FLAGS "-static" )
