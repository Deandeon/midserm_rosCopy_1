import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from maze_energy.ledger import ENERGY_COSTS, EnergyLedger


class EnergyNode(Node):
    def __init__(self) -> None:
        super().__init__("energy_node")

        self.ledger = EnergyLedger()
        self.final_report_printed = False

        self.motion_subscription = self.create_subscription(
            String, "motion_event", self.motion_event_callback, 10
        )
        self.goal_subscription = self.create_subscription(
            String, "goal_reached", self.goal_reached_callback, 10
        )
        self.energy_publisher = self.create_publisher(String, "energy_status", 10)
        self.timer = self.create_timer(1.0, self.publish_energy_status)

        self.get_logger().info("Energy node started with total budget 1000 EU.")

    def motion_event_callback(self, msg: String) -> None:
        action = msg.data.strip()
        if not action:
            return

        if action not in ENERGY_COSTS:
            self.get_logger().warn(f"Ignoring unknown motion event '{action}'.")
            return

        if not self.ledger.apply(action):
            self.get_logger().warn(
                f"Not enough energy left for '{action}'. "
                f"Remaining: {self.ledger.remaining_energy:.2f} EU"
            )
            return

        self.get_logger().info(
            f"Action: {action} | Cost: {ENERGY_COSTS[action]:.2f} EU | "
            f"Used: {self.ledger.energy_used:.2f} EU | "
            f"Remaining: {self.ledger.remaining_energy:.2f} EU"
        )

    def publish_energy_status(self) -> None:
        msg = String()
        msg.data = json.dumps(self.ledger.to_dict())
        self.energy_publisher.publish(msg)

    def goal_reached_callback(self, msg: String) -> None:
        if self.final_report_printed:
            return
        self.get_logger().info(f"Goal notification received: {msg.data}")
        self.print_final_report()
        self.final_report_printed = True

    def print_final_report(self) -> None:
        self.get_logger().info("=" * 55)
        self.get_logger().info("FINAL ENERGY REPORT")
        self.get_logger().info("=" * 55)
        self.get_logger().info(f"Total Budget  : {self.ledger.total_budget:.2f} EU")
        self.get_logger().info(f"Energy Used   : {self.ledger.energy_used:.2f} EU")
        self.get_logger().info(f"Energy Left   : {self.ledger.remaining_energy:.2f} EU")
        self.get_logger().info("-" * 55)
        self.get_logger().info("Action Breakdown:")
        for action, count in self.ledger.action_counts.items():
            if count <= 0:
                continue
            total = ENERGY_COSTS[action] * count
            self.get_logger().info(
                f"  {action:<15} count={count:<4d} cost={total:.2f} EU"
            )
        self.get_logger().info("=" * 55)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = EnergyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.print_final_report()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
