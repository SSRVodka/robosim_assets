
import os

import launch
import launch.event_handlers
import launch.launch_description_sources
import launch_ros
import launch_ros.parameter_descriptions
from ament_index_python.packages import get_package_share_directory

PKG_NAME = 'diffdrive_car_gz'
URDF_FILENAME = "robot.urdf.xacro"
WORLD_NAME = "empty.sdf"
GAZEBO_BRIDGE_CONFIG_NAME = "gz_bridge.yaml"


def generate_launch_description() -> launch.LaunchDescription:
    pkg_shared_dir = get_package_share_directory(PKG_NAME)
    robot_def_fn = os.path.join(pkg_shared_dir, "urdf", URDF_FILENAME)
    world_path = os.path.join(pkg_shared_dir, "worlds", WORLD_NAME)

    arg_declare_handle = launch.actions.DeclareLaunchArgument(
        "robot_model", default_value=robot_def_fn, description="robot model load path")
    arg_declare_world = launch.actions.DeclareLaunchArgument(
        "world", default_value=world_path, description="world model path")
    
    cmd_result = launch.substitutions.Command(
        ['xacro ', launch.substitutions.LaunchConfiguration("robot_model")])
    robot_desc_text_param_val = launch_ros.parameter_descriptions.ParameterValue(
        cmd_result, value_type=str
    )


    gz_bridge_conf_path = os.path.join(pkg_shared_dir, "config", GAZEBO_BRIDGE_CONFIG_NAME)


    # 注：这个文件是第一次启动后，配置好 RViz 界面再保存获得的。方便下次直接打开
    # robot_config_fn = os.path.join(pkg_shared_dir, "config", CONFIG_FILENAME)
    
    action_robot_desc_pub_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_desc_text_param_val},
            {'use_sim_time': True}
        ]
    )

    # No need to use joint pub (use gazebo)
    # action_robot_desc_joint_pub_node = launch_ros.actions.Node(
    #     package='joint_state_publisher',
    #     executable='joint_state_publisher',
    # )

    # @ref: https://blog.csdn.net/ZhangRelay/article/details/141561700
    # @ref: https://gazebosim.org/docs/latest/migrating_gazebo_classic_ros2_packages/
    # ros2 launch ros_gz_sim gz_sim.launch.py
    # NOTE: delegate to another Launch Description
    action_launch_gz = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        # Controllers require Gazebo Sim to start running immediately.
        launch_arguments={
            'gz_args': ['-r -v4 ', launch.substitutions.LaunchConfiguration("world")]
        }.items(),
    )

    # @ref: https://github.com/gazebosim/ros_gz/tree/ros2/ros_gz_sim
    # @ref: https://robotics.stackexchange.com/questions/113022/ros2-jazzy-gz-ignition-harmonic-question-about-description-pkg
    action_spawn_robot_in_world = launch_ros.actions.Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'voxelsky_robot',
            # '-allow_renaming', 'true',
            # '-x', "0.0",
            # '-y', "0.0",
            # '-z', "0.0",
            # '-R', "0.0",
            # '-P', "0.0",
            # '-Y', "0.0"
        ]
    )

    # @ref: https://ibrahimmansur4.medium.com/creating-a-custom-differential-drive-robot-in-gazebo-sim-af939cd8bb97
    action_gz2ros_topic_bridge = launch_ros.actions.Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={gz_bridge_conf_path}',
        ],
    )
    # @ref: https://gazebosim.org/docs/latest/migrating_gazebo_classic_ros2_packages/
    # @ref: https://robotics.stackexchange.com/questions/113504/would-a-gazebo-harmonic-plugin-meant-to-simulate-a-rgb-d-camera-inherit-from-gz
    action_gz_cam_image_raw_bridge = launch_ros.actions.Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/depth_image', '/camera/image'],
        output='screen',
    )

    # Start controllers after Gazebo Sim creates the robot.

    action_load_joint_state_broadcaster = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'vbot_joint_state_broadcaster'],
        output='screen'
    )
    action_load_diff_drive_base_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'vbot_diff_drive_controller'],
        output='screen'
    )
    # @ref: https://articulatedrobotics.xyz/tutorials/mobile-robot/applications/adv-teleop/#stampedunstamped-twist
    action_unstamp_diff_drive_cmd_vel = launch_ros.actions.Node(
        package='twist_stamper',
        executable='twist_stamper',
        # NOTE: twist_unstamper is similar
        # executable='twist_unstamper',
        remappings=[('/cmd_vel_in','/cmd_vel'),
                    ('/cmd_vel_out','/cmd_vel_stamped')]
    )

    return launch.LaunchDescription([
        arg_declare_handle,
        arg_declare_world,
        action_robot_desc_pub_node,
        # action_robot_desc_joint_pub_node,
        action_gz2ros_topic_bridge,
        action_gz_cam_image_raw_bridge,
        action_launch_gz,
        action_spawn_robot_in_world,
        # NOTE: activate controllers after robot spawn!
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_spawn_robot_in_world,
                on_exit=[action_load_joint_state_broadcaster]
            )
        ),
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_load_joint_state_broadcaster,
                on_exit=[action_load_diff_drive_base_controller]
            )
        ),
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=action_load_diff_drive_base_controller,
                on_exit=[action_unstamp_diff_drive_cmd_vel]
            )
        )
    ])
