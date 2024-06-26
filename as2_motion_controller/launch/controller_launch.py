# Copyright 2024 Universidad Politécnica de Madrid
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
#    * Neither the name of the the copyright holder nor the names of its
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

"""Launch file for the controller manager node."""

import logging
import os
import sys
from typing import List
from xml.etree import ElementTree

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

FORMAT = '[%(levelname)s] [launch]: %(message)s'
logging.basicConfig(format=FORMAT)


def get_available_plugins(package_name: str) -> List[str]:
    """Parse plugins.xml file from package and return a list of plugins from a specific type."""
    plugins_file = os.path.join(
        get_package_share_directory(package_name),
        'plugins.xml'
    )
    root = ElementTree.parse(plugins_file).getroot()

    available_plugins = []

    # Check if the root element is a <class_libraries> or <library> tag
    if root.tag == 'class_libraries':
        # Find all elements with the tag 'library' under the root
        libraries = root.findall('library')
    elif root.tag == 'library':
        # If the root is a single <library> tag, consider it as a list itself
        libraries = [root]
    else:
        # If the root tag is neither <class_libraries> nor <library>, return empty list
        return available_plugins

    for library in libraries:
        # Extract plugin information from the 'class' tag
        classes = library.findall('class')
        for plugin_class in classes:
            plugin_type = plugin_class.attrib.get('type')
            if plugin_type:
                plugin_name = plugin_type.split('::')[0]
                available_plugins.append(plugin_name)

    return available_plugins


def get_controller_manager_node(context):
    """Return the controller manager node."""
    plugin_name = LaunchConfiguration('plugin_name').perform(context)
    if not plugin_name:
        logging.critical('Plugin not set.')
        sys.exit(1)

    parameters = [{
        'plugin_name': plugin_name,
        'use_sim_time': LaunchConfiguration('use_sim_time'),
        'plugin_available_modes_config_file': LaunchConfiguration(
            'plugin_available_modes_config_file')
    }]

    plugin_config_file = LaunchConfiguration(
        'plugin_config_file').perform(context)

    if not plugin_config_file:
        print('Finding default config file for plugin: ' + plugin_name)
        plugin_config_file = PathJoinSubstitution([
            FindPackageShare('as2_motion_controller'),
            'plugins/' + plugin_name + '/config', 'controller_default.yaml'
        ])
        print('Found default config file: plugins/' +
              plugin_name + '/config/controller_default.yaml')

    parameters.append(plugin_config_file)

    controller_config_file = LaunchConfiguration(
        'motion_controller_config_file').perform(context)

    if not controller_config_file:
        controller_config_file = PathJoinSubstitution([
            FindPackageShare('as2_motion_controller'),
            'config', 'motion_controller_default.yaml'
        ])

    parameters.append(controller_config_file)

    node = Node(
        package='as2_motion_controller',
        executable='as2_motion_controller_node',
        namespace=LaunchConfiguration('namespace'),
        parameters=parameters,
        output='screen',
        emulate_tty=True
    )

    return [node]


def generate_launch_description():
    """Return the launch description."""
    launch_description = LaunchDescription([
        DeclareLaunchArgument('namespace'),
        DeclareLaunchArgument(
            'motion_controller_config_file', default_value=''),
        DeclareLaunchArgument(
            'plugin_name', choices=get_available_plugins('as2_motion_controller')),
        DeclareLaunchArgument('plugin_config_file', default_value=''),
        DeclareLaunchArgument(
            'plugin_available_modes_config_file', default_value=''),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        OpaqueFunction(function=get_controller_manager_node)
    ])

    return launch_description
