import math
import select
import sys
import termios
import threading
import tty
from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional, Tuple

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

from maze_navigation.math_utils import (
    normalize_angle,
    quaternion_to_yaw,
    shortest_angular_distance,
)


@dataclass
class Primitive:
    name: str
    distance: float = 0.0
    angle: float = 0.0
    linear_speed: float = 0.0
    angular_speed: float = 0.0
    started: bool = False
    start_x: float = 0.0
    start_y: float = 0.0
    start_yaw: float = 0.0


class MazeFinderNode(Node):
    def __init__(self) -> None:
        super().__init__("maze_finder_node")

        self.start_key = self.declare_parameter("start_key", "s").value.lower()
        self.cell_size = float(self.declare_parameter("cell_size", 0.30).value)
        self.forward_speed = float(self.declare_parameter("forward_speed", 0.10).value)
        self.turn_speed = float(self.declare_parameter("turn_speed", 0.60).value)
        self.position_tolerance = float(
            self.declare_parameter("position_tolerance", 0.03).value
        )
        self.angle_tolerance = float(self.declare_parameter("angle_tolerance", 0.07).value)
        self.wall_threshold = float(self.declare_parameter("wall_threshold", 0.40).value)
        self.clear_threshold = float(self.declare_parameter("clear_threshold", 0.55).value)
        self.sector_half_width_deg = float(
            self.declare_parameter("sector_half_width_deg", 18.0).value
        )
        self.use_goal_cell = bool(self.declare_parameter("use_goal_cell", False).value)
        self.goal_cell_x = int(self.declare_parameter("goal_cell_x", 0).value)
        self.goal_cell_y = int(self.declare_parameter("goal_cell_y", 0).value)
        self.goal_x = float(self.declare_parameter("goal_x", 2.0).value)
        self.goal_y = float(self.declare_parameter("goal_y", 2.0).value)
        self.goal_tolerance = float(self.declare_parameter("goal_tolerance", 0.20).value)

        self.scan: Optional[LaserScan] = None
        self.odom: Optional[Odometry] = None
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.origin_x: Optional[float] = None
        self.origin_y: Optional[float] = None
        self.started = False
        self.goal_reached = False
        self.goal_announced = False
        self.action_queue: Deque[Primitive] = deque()
        self.active_primitive: Optional[Primitive] = None
        self.detected_gems = []

        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.motion_event_pub = self.create_publisher(String, "motion_event", 10)
        self.goal_pub = self.create_publisher(String, "goal_reached", 10)

        self.create_subscription(LaserScan, "scan", self.scan_callback, 10)
        self.create_subscription(Odometry, "odom", self.odom_callback, 10)
        self.create_subscription(String, "gem_detection", self.gem_callback, 10)

        self.control_timer = self.create_timer(0.05, self.control_loop)

        self._keyboard_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        self._keyboard_thread.start()

        self.get_logger().info("Maze finder ready. Press 'S' in the terminal to start.")

    def scan_callback(self, msg: LaserScan) -> None:
        self.scan = msg

    def odom_callback(self, msg: Odometry) -> None:
        self.odom = msg
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.current_yaw = quaternion_to_yaw(
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w,
        )
        if self.origin_x is None:
            self.origin_x = self.current_x
            self.origin_y = self.current_y

    def gem_callback(self, msg: String) -> None:
        if msg.data and msg.data not in self.detected_gems:
            self.detected_gems.append(msg.data)
            self.get_logger().info(f"Gem recorded: {msg.data}")

    def _keyboard_listener(self) -> None:
        if not sys.stdin.isatty():
            self.get_logger().warn(
                "Keyboard start gate needs a terminal. Node will stay idle until started manually."
            )
            return

        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while rclpy.ok() and not self.started:
                ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not ready:
                    continue
                key = sys.stdin.read(1).lower()
                if key == self.start_key:
                    self.started = True
                    self.get_logger().info("Start key received. Maze solving started.")
        except Exception as exc:  # pragma: no cover
            self.get_logger().error(f"Keyboard listener failed: {exc}")
        finally:  # pragma: no cover
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def publish_motion_event(self, action: str) -> None:
        msg = String()
        msg.data = action
        self.motion_event_pub.publish(msg)

    def publish_goal_message(self) -> None:
        goal_cell = self.current_cell()
        gem_summary = ", ".join(self.detected_gems) if self.detected_gems else "none"
        msg = String()
        msg.data = (
            f"goal_reached cell={goal_cell} "
            f"world=({self.current_x:.2f},{self.current_y:.2f}) "
            f"gems=[{gem_summary}]"
        )
        self.goal_pub.publish(msg)

    def current_cell(self) -> Tuple[int, int]:
        if self.origin_x is None or self.origin_y is None:
            return (0, 0)
        cx = int(round((self.current_x - self.origin_x) / self.cell_size))
        cy = int(round((self.current_y - self.origin_y) / self.cell_size))
        return (cx, cy)

    def angle_distance(self) -> float:
        if not self.active_primitive:
            return 0.0
        return shortest_angular_distance(
            self.active_primitive.start_yaw,
            self.current_yaw,
        )

    def linear_distance(self) -> float:
        if not self.active_primitive:
            return 0.0
        dx = self.current_x - self.active_primitive.start_x
        dy = self.current_y - self.active_primitive.start_y
        return math.hypot(dx, dy)

    def sector_min_range(self, center_deg: float, half_width_deg: float) -> float:
        if self.scan is None:
            return float("inf")

        best = float("inf")
        center = math.radians(center_deg)
        half = math.radians(half_width_deg)

        for i, r in enumerate(self.scan.ranges):
            if math.isinf(r) or math.isnan(r):
                continue
            angle = self.scan.angle_min + i * self.scan.angle_increment
            if abs(normalize_angle(angle - center)) <= half:
                best = min(best, r)
        return best

    def is_goal_reached(self) -> bool:
        if self.use_goal_cell:
            return self.current_cell() == (self.goal_cell_x, self.goal_cell_y)
        return math.hypot(self.current_x - self.goal_x, self.current_y - self.goal_y) <= self.goal_tolerance

    def enqueue(self, primitive: Primitive) -> None:
        self.action_queue.append(primitive)

    def enqueue_move_forward(self) -> None:
        self.enqueue(Primitive("move_forward", distance=self.cell_size, linear_speed=abs(self.forward_speed)))

    def enqueue_move_backward(self) -> None:
        self.enqueue(Primitive("move_backward", distance=self.cell_size, linear_speed=-abs(self.forward_speed)))

    def enqueue_turn_left(self) -> None:
        self.enqueue(Primitive("turn_left", angle=math.pi / 2.0, angular_speed=abs(self.turn_speed)))

    def enqueue_turn_right(self) -> None:
        self.enqueue(Primitive("turn_right", angle=-math.pi / 2.0, angular_speed=-abs(self.turn_speed)))

    def enqueue_turn_around(self) -> None:
        self.enqueue(Primitive("rotate_180", angle=math.pi, angular_speed=abs(self.turn_speed)))

    def stop_robot(self) -> None:
        self.cmd_pub.publish(Twist())

    def plan_next_actions(self) -> None:
        left = self.sector_min_range(90.0, self.sector_half_width_deg)
        front = self.sector_min_range(0.0, self.sector_half_width_deg)
        right = self.sector_min_range(-90.0, self.sector_half_width_deg)

        left_clear = left > self.clear_threshold
        front_clear = front > self.clear_threshold
        right_clear = right > self.clear_threshold

        self.get_logger().info(
            f"Decision scan front={front:.2f} left={left:.2f} right={right:.2f} cell={self.current_cell()}"
        )

        if left_clear:
            self.enqueue_turn_left()
            self.enqueue_move_forward()
        elif front_clear:
            self.enqueue_move_forward()
        elif right_clear:
            self.enqueue_turn_right()
            self.enqueue_move_forward()
        else:
            self.enqueue_turn_around()
            self.enqueue_move_forward()

    def start_primitive(self, primitive: Primitive) -> None:
        primitive.started = True
        primitive.start_x = self.current_x
        primitive.start_y = self.current_y
        primitive.start_yaw = self.current_yaw

        self.publish_motion_event("start_moving")
        self.publish_motion_event(primitive.name)
        self.get_logger().info(f"Executing primitive: {primitive.name}")

    def execute_primitive(self, primitive: Primitive) -> bool:
        if not primitive.started:
            self.start_primitive(primitive)

        cmd = Twist()

        if primitive.name in ("move_forward", "move_backward"):
            travelled = self.linear_distance()
            if travelled >= max(0.0, primitive.distance - self.position_tolerance):
                self.stop_robot()
                self.publish_motion_event("stop_moving")
                self.get_logger().info(f"Completed primitive: {primitive.name}")
                return True
            cmd.linear.x = primitive.linear_speed

        elif primitive.name in ("turn_left", "turn_right", "rotate_180"):
            rotated = self.angle_distance()
            if abs(rotated) >= max(0.0, abs(primitive.angle) - self.angle_tolerance):
                self.stop_robot()
                self.publish_motion_event("stop_moving")
                self.get_logger().info(f"Completed primitive: {primitive.name}")
                return True
            cmd.angular.z = primitive.angular_speed

        self.cmd_pub.publish(cmd)
        return False

    def control_loop(self) -> None:
        if self.odom is None or self.scan is None:
            return

        if not self.started:
            self.stop_robot()
            return

        if self.goal_reached:
            self.stop_robot()
            if not self.goal_announced:
                self.goal_announced = True
                self.publish_goal_message()
                self.get_logger().info(
                    f"Goal reached at cell={self.current_cell()} world=({self.current_x:.2f}, {self.current_y:.2f}). "
                    "Node will remain alive until killed."
                )
                if self.detected_gems:
                    self.get_logger().info(f"Detected gems in order: {self.detected_gems}")
            return

        if self.is_goal_reached():
            self.goal_reached = True
            return

        if self.active_primitive is None and self.action_queue:
            self.active_primitive = self.action_queue.popleft()

        if self.active_primitive is not None:
            done = self.execute_primitive(self.active_primitive)
            if done:
                self.active_primitive = None
            return

        self.plan_next_actions()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MazeFinderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Maze finder interrupted by user.")
        node.stop_robot()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
