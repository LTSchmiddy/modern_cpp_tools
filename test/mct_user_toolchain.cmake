# D:/git-repos/modern_cpp_tools/test/mct_user_toolchain.cmake
# Project toolchain file generated by MCT. 
#
# The lines ending with the comments `#-global-toolchain`, `#-global-include`, `#-local-toolchain`, and `#-local-include` include the toolchains
# for the global and local copies of vcpkg. If MCT needs to update where these files are located, these 
# comments are used to locate these include statements in the file.
#
# Don't remove these comments or add anything after them, or else MCT will not detect the comments. 
# If the comments are not detected, these include lines be added (commented out) to the top of the file.
#
# Additionally, don't include anything else on these lines, otherwise MCT may remove your changes. 
# You may, however comment one of the lines out to disable that toolchain. MCT will watch for this and
# preserve that commented state if it needs to changes the paths.
#
# Otherwise, you may edit these file however you wish.
# =======================================================================================================

# Global toolchain is disabled by default:
# include("D:/git-repos/modern_cpp_tools/vcpkg/scripts/buildsystems/vcpkg.cmake") #-global-toolchain
# set(GLOBAL_TRIPLET_INCLUDE_DIR D:/git-repos/modern_cpp_tools/vcpkg/installed/${VCPKG_TARGET_TRIPLET}/include) #-global-include
# include_directories(${GLOBAL_TRIPLET_INCLUDE_DIR})

# Local toolchain:
include("D:/git-repos/modern_cpp_tools/test/vcpkg/scripts/buildsystems/vcpkg.cmake") #-local-toolchain
set(LOCAL_TRIPLET_INCLUDE_DIR D:/git-repos/modern_cpp_tools/test/vcpkg/installed/${VCPKG_TARGET_TRIPLET}/include) #-local-include
include_directories(${LOCAL_TRIPLET_INCLUDE_DIR})
