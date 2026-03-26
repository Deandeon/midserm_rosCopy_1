from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare("rover_description")
    gazebo_share = FindPackageShare("gazebo_ros")
    xacro_file = PathJoinSubstitution([pkg_share, "urdf", "rover.urdf.xacro"])

    robot_description = {
        "robot_description": Command(["xacro", 
        " ",xacro_file])
    }

    gazebo_launch = PathJoinSubstitution([gazebo_share, "launch", "gazebo.launch.py"])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch)
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[robot_description],
            output="screen"
        ),
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=["-entity", "rover", "-topic", "robot_description"],
            output="screen"
        )
    ])
