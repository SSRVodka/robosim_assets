import os

import launch
import launch_ros
import launch_ros.parameter_descriptions
from ament_index_python.packages import get_package_share_directory

PKG_NAME = "diffdrive_car_desc"
URDF_FILENAME = "robot.urdf.classic.xacro"


def generate_launch_description() -> launch.LaunchDescription:
    pkg_shared_dir = get_package_share_directory(PKG_NAME)
    robot_def_fn = os.path.join(pkg_shared_dir, "urdf", URDF_FILENAME)
    robot_model = launch.substitutions.LaunchConfiguration("robot_model")
    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        launch.substitutions.Command(["xacro ", robot_model]), value_type=str
    )

    return launch.LaunchDescription(
        [
            launch.actions.DeclareLaunchArgument(
                "robot_model", default_value=robot_def_fn, description="robot model load path"
            ),
            launch_ros.actions.Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description}],
            ),
            launch_ros.actions.Node(
                package="joint_state_publisher",
                executable="joint_state_publisher",
            ),
            launch_ros.actions.Node(package="rviz2", executable="rviz2"),
        ]
    )
