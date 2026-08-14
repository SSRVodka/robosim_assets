#!/usr/bin/env python3
# launch: gazebo classic, navigation2 with robot & framework

import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from robot_sim_common import config

# current package
PKG_NAME = "demos"

DEFAULT_ROBOT_NAME = "diffdrive_car"
DEFAULT_ROBOT_SIM_LAUNCH_SCRIPT = "gzsim.classic.launch.py"
DEFAULT_ROBOT_NAV2_CONFIG = "nav2_params.classic.yaml"

DEFAULT_ASSET_GZ_WORLD = "standard_room.classic.world"
DEFAULT_ASSET_SLAM2D_MAP = "standard_map.yaml"
# DEFAULT_ASSET_GZ_WORLD = "aws_no_roof_small_warehouse.world"
# DEFAULT_ASSET_SLAM2D_MAP = "005/map.yaml"


def launch_setup(context: launch.LaunchContext, *args, **kwargs):
    # get the actual string of substitutions
    robot_name = context.perform_substitution(LaunchConfiguration("robot_name"))
    robot_sim_launch_script = context.perform_substitution(
        LaunchConfiguration("robot_sim_launch_script")
    )
    nav2_params = context.perform_substitution(LaunchConfiguration("nav2_params"))
    world = context.perform_substitution(LaunchConfiguration("world"))
    slam2d_map = context.perform_substitution(LaunchConfiguration("map"))
    gui = context.perform_substitution(LaunchConfiguration("gui"))

    if not config.is_robot_navigable(robot_name):
        raise RuntimeError(
            f"robot '{robot_name}' is not navigable:"
            f" please create package '{config.get_robot_nav2_pkgname(robot_name)}'"
            f" and configure your robot with '{config.get_robot_nav2_params_file_pattern()}'"
        )

    # # set env for simulator
    # os.environ["MACHINE_TYPE"] = "JetRover_Acker"
    # os.environ["LIDAR_TYPE"] = "A1"
    # os.environ["CAMERA_TYPE"] = "HP60C"

    robot_nav2_share_dir = config.get_robot_nav2_share_dir(robot_name)
    robot_desc_share_dir = config.get_robot_description_share_dir(robot_name)

    action_sim_launch = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_desc_share_dir, "launch", robot_sim_launch_script)
        ),
        launch_arguments={
            "world": os.path.join(config.ASSET_GZ_WORLDS_DIR, world),
            "gui": gui,
        }.items(),
    )
    action_nav2_and_rviz2_launch = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(PKG_NAME), "launch", "_nav2.template.launch.py"
            )
        ),
        launch_arguments={
            "map": os.path.join(config.ASSET_SLAM2D_MAPS_DIR, slam2d_map),
            "params_file": os.path.join(robot_nav2_share_dir, "config", nav2_params),
        }.items(),
    )

    # action_framwork_launch = launch.actions.IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(
    #             get_package_share_directory('control_svc'),
    #             'launch',
    #             'control_svc.launch.py')
    #     )
    # )

    delayed_nav2 = TimerAction(
        period=10.0,  # 等待sim启动5秒后执行
        actions=[action_nav2_and_rviz2_launch]
    )

    # sim-5s->nav2-8s->init-pose
    initial_pose_pub = TimerAction(
        period=20.0,
        actions=[
            Node(
                package=PKG_NAME,
                executable="pose_initialization",
                name="initial_pose_publisher",
                arguments=[],
                output="screen",
            )
        ],
    )

    return [
        # Start the sequence
        action_sim_launch,
        delayed_nav2,
        # action_framwork_launch
        initial_pose_pub
    ]


def generate_launch_description() -> launch.LaunchDescription:

    return launch.LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_name", default_value=DEFAULT_ROBOT_NAME, description="The name of the robot"
            ),
            DeclareLaunchArgument(
                "robot_sim_launch_script",
                default_value=DEFAULT_ROBOT_SIM_LAUNCH_SCRIPT,
                description="The custom simulation env (like gazebo) launch script for your robot",
            ),
            DeclareLaunchArgument(
                "nav2_params",
                default_value=DEFAULT_ROBOT_NAV2_CONFIG,
                description="The custom navigation2 configurations (robot related)",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=DEFAULT_ASSET_GZ_WORLD,
                description="The custom world for simulation env (like gazebo)",
            ),
            DeclareLaunchArgument(
                "map",
                default_value=DEFAULT_ASSET_SLAM2D_MAP,
                description="The custom SLAM 2D map for navigation2 & simulation env (like gazebo)",
            ),
            DeclareLaunchArgument(
                "gui", default_value="true", description="Start the Gazebo Classic GUI"
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
