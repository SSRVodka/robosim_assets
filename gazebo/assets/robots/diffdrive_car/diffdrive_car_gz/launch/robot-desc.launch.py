
import launch
import launch_ros

from ament_index_python.packages import get_package_share_directory

import os

import launch_ros.parameter_descriptions

PKG_NAME = 'diffdrive_car_gz'
URDF_FILENAME = "robot.urdf.xacro"
# CONFIG_FILENAME = "my_robot.rviz"


def generate_launch_description() -> launch.LaunchDescription:
    pkg_shared_dir = get_package_share_directory(PKG_NAME)
    robot_def_fn = os.path.join(pkg_shared_dir, "urdf", URDF_FILENAME)

    arg_declare_handle = launch.actions.DeclareLaunchArgument(
        "robot_model", default_value=robot_def_fn, description="robot model load path")

    cmd_result = launch.substitutions.Command(
        ['xacro ', launch.substitutions.LaunchConfiguration("robot_model")])
    robot_desc_text_param_val = launch_ros.parameter_descriptions.ParameterValue(cmd_result, value_type=str)


    # 注：这个文件是第一次启动后，配置好 RViz 界面再保存获得的。方便下次直接打开
    # robot_config_fn = os.path.join(pkg_shared_dir, "config", CONFIG_FILENAME)

    action_robot_desc_pub_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_desc_text_param_val}
        ]
    )

    action_robot_desc_joint_pub_node = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
    )

    action_robot_desc_rviz = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        # arguments=['-d', robot_config_fn],
    )

    return launch.LaunchDescription([
        arg_declare_handle,
        action_robot_desc_pub_node,
        action_robot_desc_joint_pub_node,
        action_robot_desc_rviz,
    ])
