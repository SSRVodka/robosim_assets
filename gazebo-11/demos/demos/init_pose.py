
import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node


class InitialPosePublisher(Node):
    def __init__(self) -> None:
        super().__init__('initial_pose_publisher')
        self.pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.timer = self.create_timer(1.0, self.publish_once)
        self.published = False

    def publish_once(self) -> None:
        if self.published:
            return

        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()

        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.orientation.w = 1.0

        msg.pose.covariance[0] = 0.25
        msg.pose.covariance[7] = 0.25
        msg.pose.covariance[35] = 0.0685

        self.pub.publish(msg)
        self.get_logger().info("#####################################")
        self.get_logger().info('##### Initial pose published')
        self.get_logger().info("#####################################")

        self.published = True
        self.destroy_timer(self.timer)

def main() -> None:
    rclpy.init()
    node = InitialPosePublisher()
    while rclpy.ok() and not node.published:
        rclpy.spin_once(node, timeout_sec=1.0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
