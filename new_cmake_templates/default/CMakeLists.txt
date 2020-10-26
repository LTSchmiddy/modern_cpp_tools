cmake_minimum_required(VERSION 3.0.0)
project(test VERSION 0.1.0)

set(TARGET_NAME test)

set(Boost_USE_STATIC_LIBS OFF) 
set(Boost_USE_MULTITHREADED ON)  
set(Boost_USE_STATIC_RUNTIME OFF) 

# If you're using Boost:
# find_package(Boost 1.45.0 COMPONENTS filesystem) 
# if(Boost_FOUND)
    # include_directories(${Boost_INCLUDE_DIRS}) 

add_executable(${TARGET_NAME} test.cpp)
# add_library(${TARGET_NAME} SHARED test.cpp)
# add_library(${TARGET_NAME} test.cpp)

    # target_link_libraries(${TARGET_NAME} ${Boost_LIBRARIES})
# endif()

set_target_properties(${TARGET_NAME}
    PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "./arc/"
    LIBRARY_OUTPUT_DIRECTORY "./lib/"
    RUNTIME_OUTPUT_DIRECTORY "./bin/"
)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
