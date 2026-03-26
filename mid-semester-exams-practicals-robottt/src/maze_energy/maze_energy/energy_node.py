import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import json


class EnergyNode(Node):
    def __init__(self):
        super().__init__("energy_node")

        # Energy Budget
        self.total_budget = 1000.0
        self.energy_used = 0.0

        # Energy cost for each action 
        self.energy_costs = {
            "move_forward": 5.0,
            "move_backward": 8.0,
            "turn_left": 3.0,
            "turn_right": 3.0,
            "rotate_180": 6.0,
            "start_moving": 1.0,
            "stop_moving": 0.5,
        }

        # Count the number of time each action was performed
        self.action_counts = {
            "move_forward": 0,
            "move_backward": 0,
            "turn_left": 0,
            "turn_right": 0,
            "rotate_180": 0,
            "start_moving": 0,
            "stop_moving": 0,
        }

        # Track if the robot was moving in the pre cmd
        self.was_moving = False

        
        self.cmd_subscription = self.create_subscription(
            Twist,
            "cmd_vel",
            self.cmd_vel_callback,
            10
        )

        # When the navigator signals that the goal is reached, print the final report
        self.goal_subscription = self.create_subscription(
            String,
            "goal_reached",
            self.goal_reached_callback,
            10
        )

        # Publish energy status every second so other nodes can read it
        self.energy_publisher = self.create_publisher(
            String, "energy_status", 10)
        self.timer = self.create_timer(1.0, self.publish_energy_status)

        self.get_logger().info("Energy node is running. Total budget: 1000 EU")

    def cmd_vel_callback(self, msg):
    
        linear = msg.linear.x    # forward or backward speed
        angular = msg.angular.z  # turning speed

        # Check if the robot is stopped
        if linear == 0.0 and angular == 0.0:
            if self.was_moving:
                self.deduct_energy("stop_moving")
                self.was_moving = False
            return

        # Robot moving, charge start cost if it was stopped before
        if not self.was_moving:
            self.deduct_energy("start_moving")
            self.was_moving = True

        if linear > 0.0 and angular == 0.0:
            # Moving straight forward
            self.deduct_energy("move_forward")

        elif linear < 0.0 and angular == 0.0:
            # Moving straight backward
            self.deduct_energy("move_backward")

        elif angular > 0.0 and linear == 0.0:
            # Turning left (counter-clockwise)
            self.deduct_energy("turn_left")

        elif angular < 0.0 and linear == 0.0:
            # Turning right (clockwise)
            self.deduct_energy("turn_right")

        elif abs(angular) > 2.5 and linear == 0.0:
            # Rotating 180 degrees 
            self.deduct_energy("rotate_180")

    def deduct_energy(self, action):
        
        cost = self.energy_costs[action]
        remaining = self.total_budget - self.energy_used

        # Check if there is enough energy left
        if cost > remaining:
            self.get_logger().warn(
                f"Not enough energy for '{action}'! "
                f"Only {remaining:.2f} EU remaining."
            )
            return

        # Deduct the cost and count the action
        self.energy_used += cost
        self.action_counts[action] += 1

        # Log what happened
        self.get_logger().info(
            f"Action: {action} | "
            f"Cost: {cost} EU | "
            f"Used so far: {self.energy_used:.2f} EU | "
            f"Remaining: {self.total_budget - self.energy_used:.2f} EU"
        )

    def publish_energy_status(self):
        status = {
            "total_budget": self.total_budget,
            "energy_used": self.energy_used,
            "energy_remaining": self.total_budget - self.energy_used,
            "action_counts": self.action_counts,
        }

        msg = String()
        msg.data = json.dumps(status)
        self.energy_publisher.publish(msg)

    def goal_reached_callback(self, msg):
        self.get_logger().info("Goal reached signal received! Printing final report...")
        self.print_final_report()

    def print_final_report(self):
        remaining = self.total_budget - self.energy_used

        self.get_logger().info("=" * 50)
        self.get_logger().info("        FINAL ENERGY REPORT")
        self.get_logger().info("=" * 50)
        self.get_logger().info(
            f"  Total Budget   : {self.total_budget:.2f} EU")
        self.get_logger().info(f"  Energy Used    : {self.energy_used:.2f} EU")
        self.get_logger().info(f"  Energy Left    : {remaining:.2f} EU")
        self.get_logger().info("-" * 50)
        self.get_logger().info("  Action Breakdown:")

        for action, count in self.action_counts.items():
            if count > 0:
                total_cost = self.energy_costs[action] * count
                self.get_logger().info(
                    f"    {action:<20} : {count} times = {total_cost:.2f} EU"
                )

        self.get_logger().info("=" * 50)


def main(args=None):
    rclpy.init(args=args)

    # Create the energy node
    energy_node = EnergyNode()

    try:
        rclpy.spin(energy_node)
    except KeyboardInterrupt:
        # If Ctrl+C is pressed, print the final report before exiting
        energy_node.print_final_report()
    finally:
        energy_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
