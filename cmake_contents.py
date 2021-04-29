#!/usr/bin python3
# coding: utf-8
"""
the contents of CMakeLists.txt
"""

ROOT_CMAKE_CONTENT = r"""
cmake_minimum_required(VERSION 3.14)
# set variable before project() to make it valid for submodules
set(CMAKE_BUILD_TYPE Debug)
# set library output path
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
# set executable output path
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

project(PROJECT_NAME VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# gtest submodule
# include(cmake/get_gtest.cmake)

# Options
option(BUILD_TESTS "Build test executable" OFF)
option(GEN_DOCS "Generate documentation" OFF)
option(ENABLE_COVERAGE "Enable code coverage" OFF)
# print verbose command
set(CMAKE_VERBOSE_MAKEFILE OFF)

# Set global property (all targets are impacted)
# set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CMAKE_COMMAND} -E time")

# project-wide cpp flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wnon-virtual-dtor -pedantic")
# project-wide include directory
include_directories(./inc)

# add_subdirectory(src)
# add_subdirectory(app)

if (BUILD_TESTS)
    include(CTest)
    enable_testing()
    add_subdirectory(test)
endif (BUILD_TESTS)

if (GEN_DOCS)
    add_subdirectory(doc)
endif (GEN_DOCS)

if(ENABLE_COVERAGE) 
    add_compile_options(-fprofile-arcs -ftest-coverage)
    set(CMAKE_EXE_LINKER_FLAGS  "${CMAKE_EXE_LINKER_FLAGS} -fprofile-arcs -ftest-coverage")
    file(COPY ./cmake/gcov DESTINATION .)
endif()
"""

# write CMakeLists.txt under src directory
LIB_CMAKE_CONTENT = r"""
set (lib LIBNAME)
#add src files 
file (GLOB SRC_LIST "./*.cc" "./*.c")
set (DEP_LIBS pthread)
#build library
add_library(${lib} ${SRC_LIST})
target_include_directories(${lib} PRIVATE .)
target_link_libraries(${lib} ${DEP_LIBS})
"""

TEST_CMAKE_CONTENT = r"""
set(DEP_LIBS gtest_main gtest pthread)

file(GLOB files "*.cc")
foreach(file ${files})
    get_filename_component(testcase ${file} NAME_WE)
    add_executable(${testcase} ${file})
	
    target_include_directories(${testcase} PRIVATE  .)
    target_link_libraries(${testcase} PRIVATE ${DEP_LIBS})
    add_test(NAME "${testcase}" COMMAND ${testcase})
endforeach()
"""

APP_CMAKE_CONTENT = r"""
set(DEP_LIBS pthread)

file(GLOB files "*.cc")
foreach(file ${files})
    get_filename_component(app ${file} NAME_WE)
    add_executable(${app} ${file})
	
    target_include_directories(${app} PRIVATE  .)
    target_link_libraries(${app} PRIVATE ${DEP_LIBS})
endforeach()
"""