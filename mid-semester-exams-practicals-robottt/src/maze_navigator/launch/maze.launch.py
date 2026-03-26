import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    rover_pkg = get_package_share_directory("rover_description")
    ashbot_pkg = get_package_share_directory("ashbot_world")

    maze_yaml_file = os.path.join(ashbot_pkg, "config", "maze.yaml")
    with open(maze_yaml_file, "r") as f:
        maze_config = yaml.safe_load(f)

    start_x = str(maze_config["start_coordinate"][0])
    start_y = str(maze_config["start_coordinate"][1])
    start_yaw = str(maze_config["start_coordinate"][2])


    xacro_file = os.path.join(rover_pkg, "urdf", "rover.urdf.xacro")
    robot_description = Command(["xacro", " ", xacro_file])

    maze_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ashbot_pkg, "launch", "maze.launch.py")
        ),
        launch_arguments={
            "vehicle_length": "0.20",
            "vehicle_width": "0.25",
            "gems": "false",
        }.items(),
    )

    
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True,
        }],
        output="screen",
    )

   
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "rover",
            "-topic", "robot_description",
            "-x", start_x,
            "-y", start_y,
            "-z", "0.18",
            "-Y", start_yaw,
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
        ],
        output="screen",
    )

    energy_node = Node(
        package="maze_energy",
        executable="energy_node",
        name="energy_node",
        output="screen",
    )

    navigator_node = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="maze_navigator",
                executable="navigator_node",
                name="maze_navigator",
                output="screen",
            )
        ]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
    )

    return LaunchDescription([
        maze_world,
        robot_state_publisher,
        spawn_robot,
        bridge,
        energy_node,
        navigator_node,
        rviz_node,
    ])