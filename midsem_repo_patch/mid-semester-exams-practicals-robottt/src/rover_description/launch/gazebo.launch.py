from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    world_file = LaunchConfiguration("world_file")
    use_rviz = LaunchConfiguration("use_rviz")
    enable_camera = LaunchConfiguration("enable_camera")
    use_gems = LaunchConfiguration("use_gems")

    description_share = FindPackageShare("rover_description")
    navigation_share = FindPackageShare("maze_navigation")
    gazebo_share = FindPackageShare("ros_gz_sim")
    world_share = FindPackageShare("ashbot_world")

    xacro_file = PathJoinSubstitution([description_share, "urdf", "rover.urdf.xacro"])
    rviz_config = PathJoinSubstitution([description_share, "rviz", "rover.rviz"])
    params_file = PathJoinSubstitution([navigation_share, "config", "maze_params.yaml"])
    world_path = PathJoinSubstitution([world_share, "worlds", world_file])

    robot_description = {
        "robot_description": Command([
            "xacro"," ",
            xacro_file,
            "use_sim:=true",
            "enable_lidar:=true",
            "enable_camera:=", enable_camera,
        ])
    }

    gazebo_launch = PathJoinSubstitution([gazebo_share, "launch", "gazebo.launch.py"])

    return LaunchDescription([
        DeclareLaunchArgument("world_file", default_value="maze.world"),
        DeclareLaunchArgument("use_rviz", default_value="true"),
        DeclareLaunchArgument("enable_camera", default_value="false"),
        DeclareLaunchArgument("use_gems", default_value="false"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch),
            launch_arguments={"world": world_path}.items(),
        ),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[robot_description],
            output="screen",
        ),

        Node(
            package="ros_gz_sim",
            executable="spawn_entity.py",
            arguments=[
                "-entity", "rover",
                "-topic", "robot_description",
                "-x", "0.0",
                "-y", "0.0",
                "-z", "0.08",
            ],
            output="screen",
        ),

        Node(
            package="maze_energy",
            executable="energy_node",
            output="screen",
        ),

        Node(
            package="maze_navigation",
            executable="maze_finder_node",
            parameters=[params_file],
            output="screen",
        ),

        Node(
            condition=IfCondition(use_gems),
            package="maze_perception",
            executable="gem_detector_node",
            parameters=[params_file],
            output="screen",
        ),

        Node(
            condition=IfCondition(use_rviz),
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_config],
            output="screen",
        ),
    ])
