import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import yaml
import os
import sys
from ament_index_python.packages import get_package_share_directory

class MazeNavigator(Node):
    def __init__(self):
        super().__init__("maze_navigator")

        # Wait for the 'S' key to be pressed before starting
        self.get_logger().info("Press 'S' to start the maze navigator...")
        self.wait_for_start()

        # Read start and end coordinates from the config YAML file
        self.start_x, self.start_y, self.start_yaw, self.end_x, self.end_y = self.read_config()

        self.get_logger().info(
            f"Start: ({self.start_x}, {self.start_y}, yaw={self.start_yaw}) | "
            f"End: ({self.end_x}, {self.end_y})"
        )

        # Robot statesss
        self.is_running = True       # True while the robot is navigating
        self.goal_reached = False    # True once robot reaches the end

        # LIDAR readingss
        self.front_distance = float("inf")  # distance from wall in front
        self.right_distance = float("inf")  # distance from wall on the right
        self.left_distance = float("inf")   # distance from wall on the left

        # Movement speeeds
        self.forward_speed = 0.15   # linear speed when moving forward
        self.turn_speed = 0.5       # angular speed when turning

        # wall following thresholds
        self.wall_distance = 0.3    # distance to maintain from the right wall
        self.too_close = 0.25       # if closer than 0.25, too close to a wall
        self.too_far = 0.45         # if farther than 0.45, too far from the wall

        # Sends movement commands to the robot
        self.cmd_publisher = self.create_publisher(Twist, "cmd_vel", 10)

        # Signals when the goal is reached
        self.goal_publisher = self.create_publisher(String, "goal_reached", 10)

        # Receives LIDAR scan data
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            "scan",
            self.scan_callback,
            10
        )

        # Receives current robot position from odometry
        self.odom_subscriber = self.create_subscription(
            Odometry,
            "odom",
            self.odom_callback,
            10
        )

        # Runs the wall following logic 10 times per second
        self.timer = self.create_timer(0.1, self.navigate)

        self.get_logger().info("Maze navigator started! Using right-hand wall following.")

    def wait_for_start(self):
        while True:
            key = input("").strip().upper()
            if key == "S":
                self.get_logger().info("'S' pressed! Starting navigation...")
                break

    def read_config(self):
        config_path = os.path.join(
            get_package_share_directory("ashbot_world"),
            "config",
            "maze.yaml"
        )

        if not os.path.exists(config_path):
            self.get_logger().error(f"Config file not found at: {config_path}")
            sys.exit(1)

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        start_x = config["start_coordinate"][0]
        start_y = config["start_coordinate"][1]
        start_yaw = config["start_coordinate"][2]

        end_x = config["end_coordinate"][0]
        end_y = config["end_coordinate"][1]

        return start_x, start_y, start_yaw, end_x, end_y

    def scan_callback(self, msg):
        ranges = msg.ranges
        num_ranges = len(ranges)

        def get_distance(index):
            value = ranges[index % num_ranges]
            if value == 0.0 or value == float("inf") or value != value:
                return float("inf")
            return value

        
        self.front_distance = min(
            get_distance(0),
            get_distance(1),
            get_distance(359)
        )

        
        self.right_distance = min(
            get_distance(269),
            get_distance(270),
            get_distance(271)
        )


        self.left_distance = min(
            get_distance(89),
            get_distance(90),
            get_distance(91)
        )

    def odom_callback(self, msg):
        # Get current robot position
        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y

        # Check if close enough to the end position
        distance_to_goal = (
            (current_x - self.end_x) ** 2 +
            (current_y - self.end_y) ** 2
        ) ** 0.5

        if distance_to_goal < 0.3 and not self.goal_reached:
            self.goal_reached = True
            self.is_running = False
            self.stop_robot()
            self.get_logger().info("Goal reached! Stopping robot.")
            self.get_logger().info("Waiting for program to be killed...")

            # Signal the energy node to print its final report
            goal_msg = String()
            goal_msg.data = "goal_reached"
            self.goal_publisher.publish(goal_msg)

    def navigate(self):
        if not self.is_running:
            return

        cmd = Twist()   

        # Right-hand wall following logic

        if self.front_distance < self.too_close:
            self.get_logger().info("Wall ahead! Turning left.")
            cmd.linear.x = 0.0
            cmd.angular.z = self.turn_speed

        elif self.right_distance > self.too_far:
            # No wall on the right, turn right to follow the wall
            self.get_logger().info("No wall on right. Turning right.")
            cmd.linear.x = self.forward_speed * 0.5
            cmd.angular.z = -self.turn_speed * 0.5

        elif self.right_distance < self.too_close:
            # Too close to the right wall, turn left a bit
            self.get_logger().info("Too close to right wall. Adjusting left.")
            cmd.linear.x = self.forward_speed * 0.5
            cmd.angular.z = self.turn_speed * 0.5

        else:
            # Good distance from right wall, move forward
            self.get_logger().info("Moving forward.")
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0

      
        self.cmd_publisher.publish(cmd)

    def stop_robot(self):
        cmd = Twist()  
        self.cmd_publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)

    # Create the navigator node
    navigator = MazeNavigator()

    try:
        # Keep the node running
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        # Stop the robot if Ctrl+C pressed
        navigator.stop_robot()
        navigator.get_logger().info("Navigator stopped.")
    finally:
        navigator.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
