# Set the minimum required CMake version
cmake_minimum_required(VERSION 3.5)

# Set the project name
set(PROJECT_NAME as2_platform_multirotor_simulator)
project(${PROJECT_NAME})

# Default to C++17 if not set
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

# Set Release as default build type if not set
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# find dependencies
set(PROJECT_DEPENDENCIES
  ament_cmake
  rclcpp
  as2_core
  as2_msgs
  std_srvs
  std_msgs
)

foreach(DEPENDENCY ${PROJECT_DEPENDENCIES})
  find_package(${DEPENDENCY} REQUIRED)
endforeach()

# Add project submodules
if(${multirotor_simulator_FOUND})
  message(STATUS "multirotor_simulator found")
else()
  message(STATUS "multirotor_simulator not found")
  include(FetchContent)
  fetchcontent_declare(
    multirotor_simulator
    GIT_REPOSITORY https://github.com/RPS98/multirotor_simulator.git
    GIT_TAG v2.0
  )
  fetchcontent_makeavailable(multirotor_simulator)
endif()

# Include necessary directories
include_directories(
  include
  include/${PROJECT_NAME}

  {EIGEN3_INCLUDE_DIRS}

  # Incluye multirotor_simulator
  ${CMAKE_BINARY_DIR}/_deps/multirotor_simulator-src/include
)

# Set source files
set(SOURCE_CPP_FILES
  src/${PROJECT_NAME}.cpp
)

# Create the node executable
add_executable(${PROJECT_NAME}_node src/${PROJECT_NAME}_node.cpp src/${PROJECT_NAME}.cpp)
ament_target_dependencies(${PROJECT_NAME}_node ${PROJECT_DEPENDENCIES})
target_link_libraries(${PROJECT_NAME}_node multirotor_simulator)

# # Create the dynamic library
# set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_library(${PROJECT_NAME} STATIC src/${PROJECT_NAME}.cpp)
ament_target_dependencies(${PROJECT_NAME} ${PROJECT_DEPENDENCIES})
target_link_libraries(${PROJECT_NAME} multirotor_simulator)

# # Set the public include directories for the library
# target_include_directories(${PROJECT_NAME} PUBLIC
# $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
# $<INSTALL_INTERFACE:include>)

# Install the headers
install(
  DIRECTORY include/
  DESTINATION include
)

# Install the node executable
install(TARGETS
  ${PROJECT_NAME}_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install the library
install(
  TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# # Export the libraries
# ament_export_libraries(${PROJECT_NAME})

# # Export the targets
# ament_export_targets(export_${PROJECT_NAME})

# # Export the include directories
# ament_export_include_directories(include)
install(DIRECTORY include/
  DESTINATION include
)

# Install the launch directory
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

# Install the config directory
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

# Tests
include(CTest)

# Build tests if testing is enabled
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  add_subdirectory(tests)
endif()

# Create the ament package
ament_package()
