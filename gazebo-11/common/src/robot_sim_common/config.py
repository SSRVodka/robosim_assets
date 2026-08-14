import glob
import os

from ament_index_python.packages import get_package_share_directory

# keep track with config.h
EMERGENCY_STOP_MARK_SVC = "/emergency_stop"
POSE_MGR_SVC = "/pose_manager/get_pose"


ASSET_MAPS_PKG_SHARED_DIR = get_package_share_directory("asset_maps")
ASSET_SLAM2D_MAPS_DIR = os.path.join(ASSET_MAPS_PKG_SHARED_DIR, "slam2d")

ASSET_WORLDS_PKG_SHARED_DIR = get_package_share_directory("asset_worlds")
ASSET_GZ_WORLDS_DIR = os.path.join(ASSET_WORLDS_PKG_SHARED_DIR, "sdf")


def get_robot_description_pkgname(robot_name: str) -> str:
    return robot_name + "_desc"


# same package as robot description
def get_robot_nav2_pkgname(robot_name: str) -> str:
    return robot_name + "_desc"


def get_robot_moveit2_pkgname(robot_name: str) -> str:
    return robot_name + "_moveit"


def get_robot_mujoco_resource_pkgname(robot_name: str) -> str:
    return robot_name + "_mujoco"


def get_robot_description_share_dir(robot_name: str) -> str:
    return get_package_share_directory(get_robot_description_pkgname(robot_name))


def get_robot_nav2_share_dir(robot_name: str) -> str:
    return get_package_share_directory(get_robot_nav2_pkgname(robot_name))


def get_robot_nav2_params_file_pattern() -> str:
    return "nav2_params*.yaml"


def get_robot_moveit2_share_dir(robot_name: str) -> str:
    return get_package_share_directory(get_robot_moveit2_pkgname(robot_name))


def get_robot_mujoco_resource_share_dir(robot_name: str) -> str:
    return get_package_share_directory(get_robot_mujoco_resource_pkgname(robot_name))


def does_robot_exist(robot_name: str) -> bool:
    return os.path.isdir(get_robot_description_share_dir(robot_name))


def is_robot_navigable(robot_name: str) -> bool:
    nav2_conf_dir = os.path.join(get_robot_nav2_share_dir(robot_name), "config")
    if not os.path.isdir(nav2_conf_dir):
        return False
    pattern = os.path.join(nav2_conf_dir, get_robot_nav2_params_file_pattern())
    matching_files = glob.glob(pattern)
    return len(matching_files) > 0


def is_robot_servo_capable(robot_name: str) -> bool:
    moveit_conf_dir = os.path.join(get_robot_moveit2_share_dir(robot_name), "config")
    if not os.path.isdir(moveit_conf_dir):
        return False
    pattern = os.path.join(moveit_conf_dir, "*.srdf")
    matching_files = glob.glob(pattern)
    return len(matching_files) > 0


def is_robot_support_mujoco(robot_name: str) -> bool:
    return os.path.exists(get_robot_mujoco_resource_share_dir(robot_name))
