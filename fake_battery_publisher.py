import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import random

class FakeBatteryPublisher(Node):
    def __init__(self):
        super().__init__('fake_battery_publisher')
        self.publisher_ = self.create_publisher(Float64, '/battery_state', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.battery = 100.0

    def timer_callback(self):
        self.battery -= random.uniform(0.1, 0.5)
        if self.battery < 0:
            self.battery = 100.0
        msg = Float64()
        msg.data = self.battery
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing battery: {msg.data:.2f}')

def main():
    rclpy.init()
    node = FakeBatteryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()