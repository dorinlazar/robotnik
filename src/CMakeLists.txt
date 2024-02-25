set(SOURCES main.cpp robotnik.cpp robotnik.hpp)

find_package(CLI11 REQUIRED)
find_package(yaml-cpp REQUIRED)

add_executable(robotnikpp ${SOURCES})

target_link_libraries(robotnikpp PRIVATE CLI11::CLI11 dpp yaml-cpp)
