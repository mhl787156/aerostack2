#!/usr/bin/env python3

"""Launch as2_platform_multirotor_simulator node."""

# Copyright 2023 Universidad Politécnica de Madrid
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the Universidad Politécnica de Madrid nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__authors__ = 'Rafael Pérez Seguí'
__copyright__ = 'Copyright (c) 2022 Universidad Politécnica de Madrid'
__license__ = 'BSD-3-Clause'
__version__ = '0.1.0'

import os

from ament_index_python.packages import get_package_share_directory
import as2_core.launch_param_utils as as2_utils
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (EnvironmentVariable, LaunchConfiguration,
                                  PathJoinSubstitution)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Entrypoint."""
    # Get default platform configuration file
    package_folder = get_package_share_directory(
        'as2_platform_multirotor_simulator')
    platform_config_file = os.path.join(package_folder,
                                        'config/platform_config_file.yaml')

    control_modes = PathJoinSubstitution([
        FindPackageShare('as2_platform_multirotor_simulator'),
        'config', 'control_modes.yaml'
    ])

    simulation_config = PathJoinSubstitution([
        FindPackageShare('as2_platform_multirotor_simulator'),
        'config', 'simulation_config.yaml'
    ])

    uav_config = PathJoinSubstitution([
        FindPackageShare('as2_platform_multirotor_simulator'),
        'config', 'uav_config.yaml'
    ])

    return LaunchDescription([
        DeclareLaunchArgument('log_level', default_value='info'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('namespace',
                              default_value=EnvironmentVariable(
                                  'AEROSTACK2_SIMULATION_DRONE_ID'),
                              description='Drone namespace'),
        DeclareLaunchArgument('control_modes_file',
                              default_value=control_modes,
                              description='Platform control modes file'),
        DeclareLaunchArgument('uav_config',
                              default_value=uav_config,
                              description='UAV configuration file'),
        DeclareLaunchArgument('simulation_config',
                              default_value=simulation_config,
                              description='Simulation configuration file'),
        *as2_utils.declare_launch_arguments(
            'config_file',
            default_value=platform_config_file,
            description='Configuration file'),
        Node(
            package='as2_platform_multirotor_simulator',
            executable='as2_platform_multirotor_simulator_node',
            name='platform',
            namespace=LaunchConfiguration('namespace'),
            output='screen',
            arguments=['--ros-args', '--log-level',
                       LaunchConfiguration('log_level')],
            emulate_tty=True,
            parameters=[
                *as2_utils.launch_configuration('config_file',
                                                default_value=platform_config_file),
                {
                    'use_sim_time': LaunchConfiguration('use_sim_time'),
                    'control_modes_file': LaunchConfiguration('control_modes_file'),
                },
                LaunchConfiguration('simulation_config'),
                LaunchConfiguration('uav_config'),
            ]
        )
    ])
