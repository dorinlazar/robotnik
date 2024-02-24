cmake_minimum_required(VERSION 3.27)

# set the project name
project(robotnikpp)

# specify the C++ standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_EXPORT_COMPILE_COMMANDS True)

add_subdirectory(src)
