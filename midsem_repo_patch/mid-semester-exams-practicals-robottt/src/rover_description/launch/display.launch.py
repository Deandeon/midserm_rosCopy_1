from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare("rover_description")
    xacro_file = PathJoinSubstitution([pkg_share, "urdf", "rover.urdf.xacro"])
    rviz_config = PathJoinSubstitution([pkg_share, "rviz", "rover.rviz"])

    robot_description = {
        "robot_description": Command([
            "xacro", xacro_file,
            "use_sim:=false",
            "enable_lidar:=true",
            "enable_camera:=false",
        ])
    }

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[robot_description],
            output="screen"
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            output="screen"
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            output="screen"
        )
    ])
