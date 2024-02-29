set(SOURCES
    main.cpp
    robotnik.cpp
    robotnik.hpp
    bot_feature.hpp
    echo_feature.cpp
    echo_feature.hpp
    rss_feature.cpp
    rss_feature.hpp)

find_package(CLI11 REQUIRED)
find_package(yaml-cpp REQUIRED)

include_directories(third_party/DPP/include)

add_executable(robotnikpp ${SOURCES})

target_link_libraries(robotnikpp PRIVATE CLI11::CLI11 dpp yaml-cpp)
