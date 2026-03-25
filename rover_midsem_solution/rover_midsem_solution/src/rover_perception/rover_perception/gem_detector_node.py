import json
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class GemDetectorNode(Node):
    def __init__(self) -> None:
        super().__init__("gem_detector_node")

        self.bridge = CvBridge()
        self.cell_size = float(self.declare_parameter("cell_size", 0.30).value)
        self.min_blob_area = int(self.declare_parameter("min_blob_area", 1200).value)
        self.stable_detection_count = int(
            self.declare_parameter("stable_detection_count", 4).value
        )

        self.origin_x: Optional[float] = None
        self.origin_y: Optional[float] = None
        self.current_x = 0.0
        self.current_y = 0.0

        self.last_label = "none"
        self.label_streak = 0
        self.logged_cells = set()

        self.pub = self.create_publisher(String, "gem_detection", 10)
        self.create_subscription(Image, "/front_camera/image_raw", self.image_callback, 10)
        self.create_subscription(Odometry, "odom", self.odom_callback, 10)

        self.get_logger().info("Gem detector started.")

    def odom_callback(self, msg: Odometry) -> None:
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        if self.origin_x is None:
            self.origin_x = self.current_x
            self.origin_y = self.current_y

    def current_cell(self) -> Tuple[int, int]:
        if self.origin_x is None or self.origin_y is None:
            return (0, 0)
        cx = int(round((self.current_x - self.origin_x) / self.cell_size))
        cy = int(round((self.current_y - self.origin_y) / self.cell_size))
        return (cx, cy)

    def image_callback(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:
            self.get_logger().warn(f"Failed to decode image: {exc}")
            return

        label = self.classify(frame)
        if label == self.last_label:
            self.label_streak += 1
        else:
            self.last_label = label
            self.label_streak = 1

        if label == "none" or self.label_streak < self.stable_detection_count:
            return

        cell = self.current_cell()
        if cell in self.logged_cells:
            return

        payload = {
            "cell": list(cell),
            "gem_type": label,
        }
        out = String()
        out.data = json.dumps(payload)
        self.pub.publish(out)
        self.logged_cells.add(cell)
        self.get_logger().info(f"Gem detected: {payload}")

    def classify(self, frame: np.ndarray) -> str:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        masks: Dict[str, np.ndarray] = {
            "standard_blue": cv2.inRange(hsv, (100, 100, 80), (135, 255, 255)),
            "epic_green": cv2.inRange(hsv, (40, 80, 80), (85, 255, 255)),
            "hazard_red_1": cv2.inRange(hsv, (0, 100, 80), (10, 255, 255)),
            "hazard_red_2": cv2.inRange(hsv, (170, 100, 80), (180, 255, 255)),
        }

        red_mask = cv2.bitwise_or(masks["hazard_red_1"], masks["hazard_red_2"])
        areas = {
            "standard_blue": int(cv2.countNonZero(masks["standard_blue"])),
            "epic_green": int(cv2.countNonZero(masks["epic_green"])),
            "hazard_red": int(cv2.countNonZero(red_mask)),
        }

        label, area = max(areas.items(), key=lambda item: item[1])
        if area < self.min_blob_area:
            return "none"
        return label


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GemDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Gem detector interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
