FROM osrf/ros:humble-desktop

WORKDIR /root/

RUN apt update
RUN apt-get install apt-utils sudo software-properties-common -y

RUN sudo apt install tmux tmuxinator -y
## ROS2 utils

RUN apt install git python3-rosdep python3-pip python3-colcon-common-extensions -y
RUN apt install ros-dev-tools git -y

RUN mkdir -p /root/aerostack2_ws/src/
RUN git clone https://github.com/aerostack2/aerostack2.git -b main

RUN rosdep update
WORKDIR /root/aerostack2_ws
RUN rosdep install --from-paths src --ignore-src -r -y
RUN colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
