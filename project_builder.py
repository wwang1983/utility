#!/usr/bin python3
# coding: utf-8
"""
build a c++ cmake project
"""

import argparse
import logging
import os


class ProjectBuilder():
    """ build a c++ cmake project """

    def __init__(self):
        self.major = 0
        self.minor = 1
        self.patch = 0
        self.__parse_arg()
        return

    def __parse_arg(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--name", required=True, help="project name", dest="project_name")
        args = parser.parse_args()
        self.project_name = args.project_name
        logging.info("project_name is %s", self.project_name)

    def version(self):
        """ return the version of the class. """
        return "{}.{}.{}".format(self.major, self.minor, self.patch)

    def fill_cmake_content(self, file_handler):
        """ generate CMakeLists.txt contents. """
        content = r"""
cmake_minimum_required(VERSION 3.5)
project(PROJECT_NAME VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(BUILD_TESTS "Build test executable" OFF)
option(GEN_DOCS "Generate documentation" ON)
option(ENABLE_COVERAGE "Enable code coverage" OFF)


#set library output path
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
#set executable output path
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Set global property (all targets are impacted)
#set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CMAKE_COMMAND} -E time")

set(CMAKE_BUILD_TYPE Debug)

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
""".replace("PROJECT_NAME", self.project_name)
        file_handler.write(content)

    def build_prject(self):
        """ make directory for project """
        if os.path.exists(self.project_name):
            logging.error("project directory %s already exists", self.project_name)
            return

        os.makedirs(self.project_name)
        with open(self.project_name + os.sep + "CMakeLists.txt", 'w') as cmake_file:
            self.fill_cmake_content(cmake_file)
        for folder in ['src', 'test', 'app']:
            os.makedirs(self.project_name + os.sep + folder)
            with open(self.project_name + os.sep + folder + os.sep + "CMakeLists.txt", 'w') as cmake_file:
                pass
        for folder in ['inc', 'cmake']:
            os.makedirs(self.project_name + os.sep + folder)
        for folder in ['build']:
            os.makedirs(self.project_name + os.sep + folder)
            with open(self.project_name + os.sep + folder + os.sep + ".gitignore", 'w') as git_ignore_file:
                content = """*\n!.gitignore\n"""
                git_ignore_file.write(content)


if __name__ == "__main__":
    INSTANCE = ProjectBuilder()
    print("project name : %s"%(INSTANCE.project_name))
    print("version : %s"%(INSTANCE.version()))
    INSTANCE.build_prject()
