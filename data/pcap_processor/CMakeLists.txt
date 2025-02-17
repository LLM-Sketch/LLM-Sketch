cmake_minimum_required(VERSION 3.14)
project(pcap_processor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 REQUIRED)

find_package(PkgConfig REQUIRED)
pkg_check_modules(PCAP REQUIRED libpcap)

include_directories(${CMAKE_SOURCE_DIR}/include)

add_executable(pcap_processor src/main.cpp)

target_link_libraries(pcap_processor PRIVATE ${PCAP_LIBRARIES} pybind11::embed)

target_include_directories(pcap_processor PRIVATE ${PCAP_INCLUDE_DIRS})
