cmake_minimum_required(VERSION 3.10.2)
project(franka_panda_desc)
find_package(ament_cmake REQUIRED)

ament_package()

install(DIRECTORY config meshes urdf DESTINATION share/${PROJECT_NAME})
