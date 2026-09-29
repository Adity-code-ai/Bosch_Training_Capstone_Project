cmake_minimum_required(VERSION 3.16)
project(LdmDecisionTest LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
# For Windows: prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

include_directories(${CMAKE_SOURCE_DIR}/include)

add_library(ldm_core
    src/core/decision.cpp
)

target_include_directories(ldm_core
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
)

add_executable(ldm_decision_tests
    tests/ldm_decision_unittest.cpp
)

target_link_libraries(ldm_decision_tests
    PRIVATE
        ldm_core
        GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(ldm_decision_tests)
