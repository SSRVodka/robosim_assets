
import os
import launch
import launch.event_handlers
import launch.launch_description_sources
import launch_ros
import launch_ros.parameter_descriptions
from ament_index_python.packages import get_package_share_directory

from robot_sim_common import config


PKG_NAME = 'xl_ipads_fixed_desc'
URDF_FILENAME = "xif.classic.xacro"
# WORLD_NAME = "custom_room.classic.world"
WORLD_NAME = "huawei_room.world"


def generate_launch_description():
    pkg_shared_dir = get_package_share_directory(PKG_NAME)
    robot_def_fn = os.path.join(pkg_shared_dir, "urdf", URDF_FILENAME)
    world_path = os.path.join(config.ASSET_GZ_WORLDS_DIR, WORLD_NAME)

    arg_declare_handle = launch.actions.DeclareLaunchArgument(
        "robot_model", default_value=robot_def_fn, description="robot model load path")
    arg_declare_world = launch.actions.DeclareLaunchArgument(
        "world", default_value=world_path, description="world model path")
    
    cmd_result = launch.substitutions.Command(
        ['xacro ', launch.substitutions.LaunchConfiguration("robot_model")])
    robot_desc_text_param_val = launch_ros.parameter_descriptions.ParameterValue(cmd_result, value_type=str)

    # Robot state node
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

    ################ Gazebo Classic Startup ################

    # for external plugin .so dir
    action_set_gz_env = launch.actions.AppendEnvironmentVariable(
        'LD_LIBRARY_PATH', "/usr/lib/x86_64-linux-gnu/gazebo-11/plugins"
    )
    action_launch_gazebo_classic = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments=[
            ('world', launch.substitutions.LaunchConfiguration("world")),
            ('verbose','true'),
            ('initial_sim_time', '0')
        ]
    )

    # add robot to env
    action_spawn_robot_in_world = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'xl_ipads_fixed',
        ]
    )

    ################ Gazebo Classic Start Fin ###############

    ################# Loading ros2_control Controllers (ONLY without gazebo control plugin) #################

    action_load_joint_state_broadcaster = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
            'xl_ipads_fixed_joint_state_broadcaster'],
        output='screen'
    )

    # action_load_effort_controller = launch.actions.ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
    #          'xl_ipads_fixed_effort_controller'], 
    #     output='screen')
    
    action_load_diff_drive_base_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'xl_ipads_fixed_diff_drive_controller'], 
        output='screen')

    ################## Finish Loading ros2_control Controllers ########################
    
    return launch.LaunchDescription([
        action_set_gz_env,
        arg_declare_handle,
        arg_declare_world,
        action_robot_desc_pub_node,
        # action_robot_desc_joint_pub_node,
        action_launch_gazebo_classic,
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
    ])
