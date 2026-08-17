#!/usr/bin/env python3
# launch template: launch navigation2 & rviz2 with configurations

import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from robot_sim_common import config


def generate_launch_description() -> launch.LaunchDescription:

    bringup_official_dir = get_package_share_directory("nav2_bringup")

    rviz_config_dir = os.path.join(bringup_official_dir, "rviz", "nav2_default_view.rviz")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    map_yaml_path = LaunchConfiguration(
        "map", default=os.path.join(config.ASSET_SLAM2D_MAPS_DIR, "room.yaml")
    )
    nav2_param_path = LaunchConfiguration("params_file", default="")
    rviz = LaunchConfiguration("rviz", default="true")

    return launch.LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value=use_sim_time,
                description="Use simulation (Gazebo) clock if true",
            ),
            DeclareLaunchArgument(
                "map", default_value=map_yaml_path, description="Full path to map file to load"
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=nav2_param_path,
                description="Full path to navigation2 param file",
            ),
            DeclareLaunchArgument("rviz", default_value=rviz, description="Start RViz2"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(bringup_official_dir, "launch", "bringup_launch.py")
                ),
                launch_arguments={
                    "map": map_yaml_path,
                    "use_sim_time": use_sim_time,
                    # 'log_level': 'debug',
                    "params_file": nav2_param_path,
                }.items(),
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2_map_display_node",
                arguments=["-d", rviz_config_dir],
                parameters=[{"use_sim_time": use_sim_time}],
                output="screen",
                condition=IfCondition(rviz),
            ),
        ]
    )
