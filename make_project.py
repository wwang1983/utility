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

# parse the input parameters
def parse_input():
    """ parse input parameters """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, help="project name", dest="name")
    parser.add_argument("-p", "--path", required=False, help="project path", default='.', dest="path")
    parser.add_argument("-o", "--option", required=False, choices=['app','lib','app_cov','lib_cov'], help="project option", default='app', dest="option")
    ARGS = parser.parse_args()
    project_name = ARGS.name
    project_path = ARGS.path
    project_option = 'app'
    if 'option' in ARGS:
        project_option = ARGS.option

    script_path = os.path.dirname(os.path.realpath(__file__))

    if not os.path.isabs(project_path):
        project_path = os.path.abspath(os.path.join(script_path, project_path))

    project_path = project_path + os.sep + project_name

    print("project name is : %s, path is : %s, option is %s"%(project_name, project_path, project_option))

    if os.path.exists(project_path):
        print("error, project directory %s already exists"%(project_path))
        exit()

    sub_paths = ['inc', 'build', 'src', 'test']
    if project_option == 'app':
        sub_paths = ['inc', 'build', 'src', 'test', 'app']
    elif project_option == 'app_cov':
        sub_paths = ['inc', 'build', 'src', 'test', 'app', 'cmake']
    elif project_option == 'lib_cov':
        sub_paths = ['inc', 'build', 'src', 'test', 'cmake']
    
    return project_name, project_path, sub_paths
    

def make_project_dirs(project_name, root_path, sub_paths):
    """ make project directories under root path """
    # make root directory and write CMakeLists.txt for the project
    os.makedirs(root_path)
    # make sub directories
    for folder in sub_paths:
        os.makedirs(root_path + os.sep + folder)
        if folder == 'inc':
            os.makedirs(root_path + os.sep + folder + os.sep + project_name)

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

def write_files(project_name, root_path, sub_paths):
    """ copy files needed for the project """
    script_path = os.path.dirname(os.path.realpath(__file__))

    # write CMakeLists.txt in project root path
    with open(root_path + os.sep + "CMakeLists.txt", 'w') as cmake_file:
        cmake_file.write(ROOT_CMAKE_CONTENT.replace("PROJECT_NAME", project_name))
    # copy .clang_format to project root path
    shutil.copy(script_path + os.sep + ".clang-format", root_path)
    # write .gitignore under build directory
    if 'build' in sub_paths:
        with open(root_path + os.sep + 'build' + os.sep + ".gitignore", 'w') as git_ignore_file:
            git_ignore_file.write("""*\n!.gitignore\n""")

    if 'src' in sub_paths:
        with open(root_path + os.sep + 'src' + os.sep + "CMakeLists.txt", 'w') as cmake_file:
            cmake_file.write(LIB_CMAKE_CONTENT.replace("LIBNAME", project_name))
    
    if 'test' in sub_paths:
        with open(root_path + os.sep + 'test' + os.sep + "CMakeLists.txt", 'w') as cmake_file:
            cmake_file.write(TEST_CMAKE_CONTENT)
    
    if 'app' in sub_paths:
        with open(root_path + os.sep + 'app' + os.sep + "CMakeLists.txt", 'w') as cmake_file:
            cmake_file.write(APP_CMAKE_CONTENT)

    if 'cmake' in sub_paths:
        # copy *.cmake files to cmake directory
        cmake_files = glob.glob(script_path + os.sep + "*.cmake")
        for cmake_file in cmake_files:
            shutil.copy(cmake_file, root_path + os.sep + "cmake" + os.sep)

        # copy gcov to cmake directory
        if os.path.exists(script_path + os.sep + "gcov"):
            shutil.copy(script_path + os.sep + "gcov", root_path + os.sep + "cmake" + os.sep)

if __name__ == "__main__":
    name, path, sub_paths = parse_input()
    make_project_dirs(name, path, sub_paths)
    write_files(name, path, sub_paths)
    print("make project %s succeed!"%name)
