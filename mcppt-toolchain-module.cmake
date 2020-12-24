# MCPPT Library to provide some additional functions aid in setup:

# message(STATUS ${CMAKE_C_COMPILER_ID})

# Additional code below:
if(MCPPT_COMPILER_ID)
    message(STATUS "MCPPT - Setting compiler id: ${MCPPT_COMPILER_ID}")
    set(CMAKE_C_COMPILER_ID ${MCCPT_COMPILER_ID})
    set(CMAKE_CXX_COMPILER_ID ${MCCPT_COMPILER_ID})
endif()

if (MCPPT_BUILD_TO_TRIPLET)
    # WINDOWS

    

endif()

function(mcppt_target_triplet TARGET_NAME)
    if (NOT VCPKG_CMAKE_SYSTEM_NAME)
        set(CMAKE_C_COMPILER_ID "msvc")
        set(CMAKE_CXX_COMPILER_ID "msvc")
        message(STATUS "MCPPT - Setting compiler id; C: ${CMAKE_C_COMPILER_ID}, CPP: ${CMAKE_CXX_COMPILER_ID}")
        set(DCMAKE_GENERATOR_PLATFORM ${VCPKG_TARGET_ARCHITECTURE})

        if(VCPKG_LIBRARY_LINKAGE EQUAL static)
            if (CMAKE_BUILD_TYPE EQUAL "DEBUG")
                target_compile_options(${TARGET_NAME} PUBLIC "/MTd")
            else ()
                target_compile_options(${TARGET_NAME} PUBLIC "/MT")
            endif ()
        elseif(VCPKG_LIBRARY_LINKAGE EQUAL dymanic)
            if (CMAKE_BUILD_TYPE EQUAL "DEBUG")
                target_compile_options(${TARGET_NAME} PUBLIC "/MDd")
            else ()
                target_compile_options(${TARGET_NAME} PUBLIC "/MD")
            endif ()
        endif()
    endif()
endfunction()
