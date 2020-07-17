#!/usr/bin python3
# coding: utf-8
"""
build a c++ cmake project

arguments:
name -- the name of the project
path -- optional, the directory of the project, could be relative or absolute,
default value is ../

after running this script, there would be a new C++ cmake project
under path directory.
"""

import argparse
import os
import glob
import shutil

VERSION = "1.0.0"

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-n", "--name", required=True, help="project name", dest="name")
PARSER.add_argument("-p", "--path", required=False, help="project path", default='../', dest="path")
ARGS = PARSER.parse_args()
PROJECT_NAME = ARGS.name
PROJECT_PATH = ARGS.path

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

if not os.path.isabs(PROJECT_PATH):
    PROJECT_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, PROJECT_PATH))

PROJECT_PATH = PROJECT_PATH + os.sep + PROJECT_NAME

print("project name is : %s, path is : %s"%(PROJECT_NAME, PROJECT_PATH))

if os.path.exists(PROJECT_PATH):
    print("error, project directory %s already exists"%(PROJECT_PATH))
    exit()

ROOT_CMAKE_CONTENT = r"""
cmake_minimum_required(VERSION 3.14)
# set variable before project() to make it valid for submodules
set(CMAKE_BUILD_TYPE Debug)
#set library output path
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
#set executable output path
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

project(PROJECT_NAME VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# gtest submodule
include(cmake/get_gtest.cmake)

# Options
option(BUILD_TESTS "Build test executable" OFF)
option(GEN_DOCS "Generate documentation" OFF)
option(ENABLE_COVERAGE "Enable code coverage" OFF)

# Set global property (all targets are impacted)
#set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CMAKE_COMMAND} -E time")

# project-wide cpp flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wnon-virtual-dtor -pedantic")
# project-wide include directory
include_directories(./include)

add_subdirectory(src)

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
""".replace("PROJECT_NAME", PROJECT_NAME)

# make root directory and write CMakeLists.txt for the project
os.makedirs(PROJECT_PATH)
with open(PROJECT_PATH + os.sep + "CMakeLists.txt", 'w') as cmake_file:
    cmake_file.write(ROOT_CMAKE_CONTENT)

# make sub directories
for folder in ['include', 'build', 'cmake', 'src', 'test', 'app']:
    os.makedirs(PROJECT_PATH + os.sep + folder)

# write .gitignore under build directory
with open(PROJECT_PATH + os.sep + 'build' + os.sep + ".gitignore", 'w') as git_ignore_file:
    git_ignore_file.write("""*\n!.gitignore\n""")

# write CMakeLists.txt under src directory
LIB_CMAKE_CONTENT = r"""
set (lib LIBNAME)
#add src files 
file (GLOB SRC_LIST "./*.cc" "./*.c")
set (DEP_LIBS pthread)
#build library
add_library(${lib} ${SRC_LIST})
target_include_directories(${lib} PRIVATE
	.
)
target_link_libraries(${lib} ${DEP_LIBS})
""".replace('LIBNAME', PROJECT_NAME)
with open(PROJECT_PATH + os.sep + 'src' + os.sep + "CMakeLists.txt", 'w') as cmake_file:
    cmake_file.write(LIB_CMAKE_CONTENT)

TEST_CMAKE_CONTENT = r"""
set(DEP_LIBS gtest_main gtest pthread)

file(GLOB files "*.cc")
foreach(file ${files})
    get_filename_component(testcase ${file} NAME_WE)
    add_executable(${testcase} ${file})
	
    target_include_directories(${testcase} PRIVATE
        .
    )
    target_link_libraries(${testcase} PRIVATE ${DEP_LIBS})
    add_test(NAME "${testcase}" COMMAND ${testcase})
endforeach()
"""
with open(PROJECT_PATH + os.sep + 'test' + os.sep + "CMakeLists.txt", 'w') as cmake_file:
    cmake_file.write(TEST_CMAKE_CONTENT)

# copy *.cmake files to cmake directory
CMAKE_MODULE_FILES = glob.glob(SCRIPT_PATH + os.sep + "*.cmake")
for cmake_file in CMAKE_MODULE_FILES:
    shutil.copy(cmake_file, PROJECT_PATH + os.sep + "cmake" + os.sep)

print("make project %s succeed!"%PROJECT_NAME)
