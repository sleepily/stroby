cmake_minimum_required(VERSION 3.21)
project(stroby)

# Find the required Qt modules
find_package(Qt6 REQUIRED COMPONENTS Core)

# Add your executable and link with Qt
add_executable(stroby src/main.rs)
target_link_libraries(stroby PRIVATE Qt6::Core)