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
from cmake_contents import *

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
