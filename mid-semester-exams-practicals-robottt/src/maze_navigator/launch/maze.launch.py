import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    rover_pkg    = get_package_share_directory("rover_description")
    ashbot_pkg   = get_package_share_directory("ashbot_world")

    # Robot URDF via xacro
    xacro_file = os.path.join(rover_pkg, "urdf", "rover.urdf.xacro")
    robot_description = Command(["xacro ", xacro_file])

    # 1. Launch the maze world in Gazebo
    maze_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ashbot_pkg, "launch", "maze.launch.py")
        ),
        launch_arguments={
            "vehicle_length": "0.20",
            "vehicle_width":  "0.25",
            "gems":           "false",
        }.items(),
    )

    # 2. Robot state publisher
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

    # 3. Spawn the robot in Gazebo
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "rover",
            "-topic", "robot_description",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.1",
            "-Y", "0.0",
        ],
        output="screen",
    )

    # 4. Bridge between Gazebo and ROS2
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
        ],
        output="screen",
    )

    # 5. Energy consumption node 
    energy_node = Node(
        package="maze_energy",
        executable="energy_node",
        name="energy_node",
        output="screen",
    )

    # 6. Navigator node
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

    # 7. RViz for visualization
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
    )

    return LaunchDescription([
        maze_world,              # 1. Launch Gazebo maze world
        robot_state_publisher,   # 2. Publish robot transforms
        spawn_robot,             # 3. Spawn robot in Gazebo
        bridge,                  # 4. Bridge Gazebo ROS2 topics
        energy_node,             # 5. Start energy tracking
        navigator_node,          # 6. Start navigator after 10s
        rviz_node,               # 7. Open RViz
    ])